  async function setLanguage(lang) {
    const res = await fetch(`/static/lang/${lang}.json`);
    const translations = await res.json();

    document.querySelectorAll('[data-i18n]').forEach((el) => {
      const key = el.getAttribute('data-i18n');
    if (translations.hasOwnProperty(key)) 
      {
        el.innerText = translations[key];
      }

    });
  }