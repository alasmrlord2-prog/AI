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
              // Default to light mode if no preference saved
              const shouldBeDark = saved === 'dark';
              
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

