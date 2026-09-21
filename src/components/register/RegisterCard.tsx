import { Link } from "@tanstack/react-router";
import { motion } from "framer-motion";
import {
  ArrowRight,
  BadgeCheck,
  Briefcase,
  Building2,
  Fingerprint,
  Loader2,
  Mail,
  Phone,
  User,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import { toast } from "sonner";
import { checkEmailAvailability } from "@/lib/api";
import { InputField } from "./InputField";
import { PasswordInput, getPasswordChecks, passwordStrong } from "./PasswordInput";
import { REGISTER_ROLES, RoleSelect } from "./RoleSelect";

const DEPARTMENTS = [
  "Cyber Crime",
  "Digital Forensics",
  "Intelligence",
  "Special Investigation",
  "Child Protection Unit",
];

const FULL_NAME_REGEX = /^[A-Za-z]+(?: [A-Za-z]+)*$/;
const STRICT_GMAIL_REGEX = /^[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*@gmail\.com$/i;
const PHONE_REGEX = /^[+0-9\s\-()]{7,20}$/;

type Props = {
  onSubmit: (payload: {
    full_name: string;
    email: string;
    password: string;
    confirm_password: string;
    role: string;
    department: string | null;
  }) => Promise<void>;
  submitting: boolean;
  error: string | null;
  success: string | null;
};

export function RegisterCard({ onSubmit, submitting, error, success }: Props) {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [department, setDepartment] = useState(DEPARTMENTS[0]);
  const [role, setRole] = useState<string>(REGISTER_ROLES[0]);
  const [badge, setBadge] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [terms, setTerms] = useState(false);

  const [touched, setTouched] = useState<Record<string, boolean>>({
    fullName: false,
    email: false,
    phone: false,
    password: false,
    confirm: false,
    terms: false,
  });

  const [emailChecking, setEmailChecking] = useState(false);
  const [emailServerStatus, setEmailServerStatus] = useState<{
    checkedEmail: string;
    exists: boolean;
    valid: boolean;
    message: string;
  } | null>(null);

  const [localError, setLocalError] = useState<string | null>(null);

  const markTouched = (field: string) => {
    setTouched((prev) => (prev[field] ? prev : { ...prev, [field]: true }));
  };

  // Full name validation
  const cleanName = fullName.trim();
  const isNameValid = useMemo(() => {
    return cleanName.length >= 2 && cleanName.length <= 50 && FULL_NAME_REGEX.test(cleanName);
  }, [cleanName]);

  const nameError = useMemo(() => {
    if (!cleanName) return "Please enter a valid full name.";
    if (!FULL_NAME_REGEX.test(cleanName) || cleanName.length < 2 || cleanName.length > 50) {
      return "Please enter a valid full name.";
    }
    return null;
  }, [cleanName]);

  // Strict Gmail format validation
  const cleanEmail = email.trim().toLowerCase();
  const isGmailFormatValid = useMemo(() => {
    return STRICT_GMAIL_REGEX.test(cleanEmail);
  }, [cleanEmail]);

  // Debounced server duplicate check
  const debounceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    if (!cleanEmail || !isGmailFormatValid) {
      setEmailChecking(false);
      setEmailServerStatus(null);
      return;
    }

    // If already checked this exact email, skip
    if (emailServerStatus && emailServerStatus.checkedEmail === cleanEmail) {
      return;
    }

    setEmailChecking(true);
    debounceTimerRef.current = setTimeout(async () => {
      try {
        const res = await checkEmailAvailability(cleanEmail);
        setEmailServerStatus({
          checkedEmail: cleanEmail,
          exists: res.exists,
          valid: res.valid,
          message: res.message,
        });
      } catch {
        // network or server offline, allow user to proceed to backend validation
        setEmailServerStatus({
          checkedEmail: cleanEmail,
          exists: false,
          valid: true,
          message: "Could not verify duplicate, will verify on submit.",
        });
      } finally {
        setEmailChecking(false);
      }
    }, 400);

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [cleanEmail, isGmailFormatValid, emailServerStatus]);

  const emailError = useMemo(() => {
    if (!cleanEmail) return "Please enter a valid Gmail address.";
    if (!isGmailFormatValid) return "Please enter a valid Gmail address.";
    if (
      emailServerStatus &&
      emailServerStatus.checkedEmail === cleanEmail &&
      emailServerStatus.exists
    ) {
      return "This Gmail address is already registered.";
    }
    return null;
  }, [cleanEmail, isGmailFormatValid, emailServerStatus]);

  const isEmailValid = useMemo(() => {
    return (
      isGmailFormatValid &&
      !emailChecking &&
      (!emailServerStatus ||
        (emailServerStatus.checkedEmail === cleanEmail && !emailServerStatus.exists))
    );
  }, [isGmailFormatValid, emailChecking, emailServerStatus, cleanEmail]);

  // Phone validation (optional)
  const cleanPhone = phone.trim();
  const isPhoneValid = useMemo(() => {
    if (!cleanPhone) return true;
    return PHONE_REGEX.test(cleanPhone);
  }, [cleanPhone]);

  const phoneError = useMemo(() => {
    if (cleanPhone && !PHONE_REGEX.test(cleanPhone)) {
      return "Please enter a valid phone number (e.g. +1 555 0100).";
    }
    return null;
  }, [cleanPhone]);

  // Password validation
  const passwordChecks = useMemo(() => getPasswordChecks(password), [password]);
  const isPasswordValid = useMemo(() => passwordStrong(passwordChecks), [passwordChecks]);

  const passwordError = useMemo(() => {
    if (!password) return "Password does not meet all requirements.";
    if (!isPasswordValid) return "Password does not meet all requirements.";
    return null;
  }, [password, isPasswordValid]);

  // Confirm password validation
  const isConfirmValid = useMemo(() => {
    return Boolean(confirm && confirm === password && isPasswordValid);
  }, [confirm, password, isPasswordValid]);

  const confirmError = useMemo(() => {
    if (!confirm) return "Please confirm your password.";
    if (confirm !== password) return "Passwords do not match.";
    return null;
  }, [confirm, password]);

  // Overall form validity
  const isFormValid = useMemo(() => {
    return (
      isNameValid &&
      isEmailValid &&
      !emailChecking &&
      isPhoneValid &&
      isPasswordValid &&
      isConfirmValid &&
      terms
    );
  }, [
    isNameValid,
    isEmailValid,
    emailChecking,
    isPhoneValid,
    isPasswordValid,
    isConfirmValid,
    terms,
  ]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLocalError(null);

    // Mark everything as touched
    setTouched({
      fullName: true,
      email: true,
      phone: true,
      password: true,
      confirm: true,
      terms: true,
    });

    // Guard checks and auto-focus first invalid input
    if (!isNameValid) {
      const msg = nameError || "Please enter a valid full name.";
      setLocalError(msg);
      toast.error(msg);
      document.getElementById("full_name")?.focus();
      return;
    }

    if (!isEmailValid) {
      const msg = emailError || "Please enter a valid Gmail address.";
      setLocalError(msg);
      toast.error(msg);
      document.getElementById("email")?.focus();
      return;
    }

    if (cleanPhone && !isPhoneValid) {
      const msg = phoneError || "Please enter a valid phone number.";
      setLocalError(msg);
      toast.error(msg);
      document.getElementById("phone")?.focus();
      return;
    }

    if (!isPasswordValid) {
      const msg = "Password does not meet all requirements.";
      setLocalError(msg);
      toast.error(msg);
      document.getElementById("password")?.focus();
      return;
    }

    if (!isConfirmValid) {
      const msg = confirmError || "Passwords do not match.";
      setLocalError(msg);
      toast.error(msg);
      document.getElementById("confirm_password")?.focus();
      return;
    }

    if (!terms) {
      const msg = "Please agree to the Privacy Policy and Terms of Service.";
      setLocalError(msg);
      toast.error(msg);
      document.getElementById("terms")?.focus();
      return;
    }

    const deptParts = [department];
    if (cleanPhone) deptParts.push(`Phone: ${cleanPhone}`);
    if (badge.trim()) deptParts.push(`Badge: ${badge.trim()}`);

    await onSubmit({
      full_name: cleanName,
      email: cleanEmail,
      password,
      confirm_password: confirm,
      role,
      department: deptParts.join(" · "),
    });
  }

  const displayError = localError || error;

  return (
    <motion.div
      initial={{ opacity: 0, y: 28 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className="relative w-full max-w-[560px] rounded-3xl border border-white/[0.08] bg-[rgba(15,23,42,0.75)] p-6 shadow-[0_0_80px_-20px_rgba(59,130,246,0.55)] backdrop-blur-xl sm:p-8"
    >
      <div className="absolute left-1/2 top-0 flex h-16 w-16 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border border-cyan/40 bg-[#020617] shadow-[0_0_40px_-4px_rgba(6,182,212,0.7)]">
        <Fingerprint className="h-7 w-7 text-cyan" />
      </div>

      <div className="mt-4 text-center">
        <h2 className="text-2xl font-bold tracking-tight text-slate-50">Create Your Account</h2>
        <p className="mt-2 text-sm text-slate-400">
          Join CyberShield to securely investigate and manage digital evidence.
        </p>
      </div>

      <form className="mt-7 space-y-4" onSubmit={handleSubmit} noValidate>
        {displayError && (
          <div
            role="alert"
            className="rounded-2xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300"
          >
            {displayError}
          </div>
        )}
        {success && (
          <div
            role="status"
            className="rounded-2xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-300"
          >
            {success}
          </div>
        )}

        <div className="grid gap-4 sm:grid-cols-2">
          <InputField
            id="full_name"
            label="Full Name"
            icon={User}
            name="full_name"
            required
            autoComplete="name"
            value={fullName}
            onChange={(e) => {
              setFullName(e.target.value);
              markTouched("fullName");
            }}
            onBlur={() => markTouched("fullName")}
            error={nameError}
            success="✓ Valid full name"
            isValid={isNameValid}
            isTouched={touched.fullName}
            placeholder="Alex Mercer"
          />

          <InputField
            id="email"
            label="Gmail Address"
            icon={Mail}
            name="email"
            type="email"
            required
            autoComplete="email"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value);
              markTouched("email");
            }}
            onBlur={() => markTouched("email")}
            error={emailError}
            success="✓ Valid Gmail address"
            isValid={isEmailValid}
            isTouched={touched.email}
            isLoading={emailChecking}
            placeholder="officer@gmail.com"
          />

          <InputField
            id="phone"
            label="Phone Number (optional)"
            icon={Phone}
            name="phone"
            type="tel"
            autoComplete="tel"
            value={phone}
            onChange={(e) => {
              setPhone(e.target.value);
              markTouched("phone");
            }}
            onBlur={() => markTouched("phone")}
            error={phoneError}
            success={cleanPhone ? "✓ Valid phone number" : null}
            isValid={isPhoneValid}
            isTouched={touched.phone}
            placeholder="+1 555 0100"
          />

          <label className="block space-y-1.5">
            <span className="text-xs font-medium text-slate-300">Department</span>
            <span className="relative block">
              <Building2 className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
              <select
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                className="w-full appearance-none rounded-2xl border border-white/[0.08] bg-[#0B1220] py-3 pl-10 pr-3 text-sm text-slate-50 outline-none transition focus:border-primary/60 focus:shadow-[0_0_0_3px_rgba(59,130,246,0.2)]"
              >
                {DEPARTMENTS.map((d) => (
                  <option key={d} value={d} className="bg-[#0F172A]">
                    {d}
                  </option>
                ))}
              </select>
            </span>
          </label>

          <RoleSelect value={role} onChange={setRole} />

          <InputField
            id="badge"
            label="Badge Number (optional)"
            icon={BadgeCheck}
            name="badge"
            value={badge}
            onChange={(e) => setBadge(e.target.value)}
            placeholder="BADGE-00421"
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <PasswordInput
            label="Password"
            name="password"
            value={password}
            onChange={(val) => {
              setPassword(val);
              markTouched("password");
            }}
            showStrength
            error={passwordError}
            success="✓ Strong password"
            isValid={isPasswordValid}
            isTouched={touched.password}
          />

          <PasswordInput
            label="Confirm Password"
            name="confirm_password"
            value={confirm}
            onChange={(val) => {
              setConfirm(val);
              markTouched("confirm");
            }}
            error={confirmError}
            success="✓ Passwords match"
            isValid={isConfirmValid}
            isTouched={touched.confirm}
          />
        </div>

        <label
          htmlFor="terms"
          className="flex cursor-pointer items-start gap-3 rounded-2xl border border-white/[0.08] bg-white/[0.03] p-4 transition hover:border-primary/30"
        >
          <input
            id="terms"
            type="checkbox"
            checked={terms}
            onChange={(e) => {
              setTerms(e.target.checked);
              markTouched("terms");
            }}
            className="mt-0.5 h-4 w-4 rounded border-white/20 bg-[#0B1220] accent-primary"
          />
          <span className="text-sm text-slate-300">
            I agree to the{" "}
            <a href="#" className="text-cyan hover:underline">
              Privacy Policy
            </a>{" "}
            and{" "}
            <a href="#" className="text-cyan hover:underline">
              Terms
            </a>
            .
          </span>
        </label>

        <motion.button
          type="submit"
          disabled={!isFormValid || submitting || emailChecking}
          whileHover={{ scale: !isFormValid || submitting || emailChecking ? 1 : 1.01 }}
          whileTap={{ scale: !isFormValid || submitting || emailChecking ? 1 : 0.99 }}
          className="flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-primary to-cyan py-3.5 text-sm font-semibold text-white shadow-[0_0_40px_-8px_rgba(59,130,246,0.75)] transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50 disabled:shadow-none"
        >
          {submitting ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" /> Creating account…
            </>
          ) : emailChecking ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" /> Verifying email…
            </>
          ) : (
            <>
              Create Secure Account <ArrowRight className="h-4 w-4" />
            </>
          )}
        </motion.button>

        <Link
          to="/login"
          className="flex w-full items-center justify-center gap-2 rounded-2xl border border-white/[0.12] py-3 text-sm font-semibold text-slate-100 transition hover:border-cyan/40 hover:bg-white/5 hover:shadow-[0_0_24px_-10px_rgba(6,182,212,0.6)]"
        >
          <Briefcase className="h-4 w-4 text-cyan" /> Login
        </Link>

        <p className="text-center text-sm text-slate-400">
          Already have an account?{" "}
          <Link to="/login" className="font-semibold text-cyan hover:underline">
            Login →
          </Link>
        </p>
      </form>
    </motion.div>
  );
}
