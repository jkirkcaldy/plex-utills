
// Light Mode / Dark Mode
function darkMode(el) {
    const body = document.getElementsByTagName('body')[0];

    if (!el.getAttribute("checked")) {

      localStorage.setItem('theme', 'dark');
      body.classList.add('dark');
      document.documentElement.setAttribute('data-bs-theme', 'dark')


      el.setAttribute("checked", true);

    } else if (!el.getAttribute("unchecked")) {
      document.documentElement.setAttribute('data-bs-theme', 'light')
      body.classList.remove('dark');
      localStorage.setItem('theme', 'light');    
      el.removeAttribute("checked");
    };

    console.log(localStorage.getItem('theme'))
  };



