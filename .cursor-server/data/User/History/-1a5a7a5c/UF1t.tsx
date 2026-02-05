/**
 * Theme Script - يطبق الـ theme قبل أن يتم render الصفحة
 * هذا يمنع الـ flash عند تحميل الصفحة
 */
export function ThemeScript() {
  return (
    <script
      dangerouslySetInnerHTML={{
        __html: `
          (function() {
            try {
              const saved = localStorage.getItem('theme');
              const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
              const shouldBeDark = saved === 'dark' || (!saved && prefersDark);
              
              if (shouldBeDark) {
                document.documentElement.classList.add('dark');
              } else {
                document.documentElement.classList.remove('dark');
              }
            } catch (e) {
              // Fallback to light mode if there's an error
              document.documentElement.classList.remove('dark');
            }
          })();
        `,
      }}
    />
  );
}

