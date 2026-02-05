import en from "@/locales/en/common.json";
import ar from "@/locales/ar/common.json";

export const translations = { en, ar };

export function t(locale: string, key: string) {
  const localeKey = locale as keyof typeof translations;
  if (localeKey in translations) {
    return translations[localeKey][key as keyof typeof translations[typeof localeKey]] || key;
  }
  return key;
}
