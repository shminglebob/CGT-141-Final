window.addEventListener('DOMContentLoaded', () => {
    //  Renew cookie for a year (idk if this is too long)
    document.cookie = `theme=${rootElement.dataset.theme};path=/;max-age=31536000`;
});

const navToggle = document.getElementById("nav-toggle"),
    nav = document.querySelector(".nav-links");

navToggle.addEventListener("click", () => {
    navToggle.classList.toggle("active");
    nav.classList.toggle("open");
});

const themeToggle = document.getElementById('theme-toggle'),
    overlay = document.getElementById('theme-overlay');
let swappingTheme = false;

themeToggle.addEventListener("click", () => {
    if (swappingTheme) return;

    swappingTheme = true;

    overlay.style.clipPath = '';
    overlay.style.opacity = '';
    overlay.style.backgroundColor = getComputedStyle(overlay).backgroundColor;

    overlay.animate(
        [
            { clipPath: 'circle(0% at 100% 0%)' },
            { clipPath: 'circle(200% at 100% 0%)' }
        ],
        {
            duration: 300,
            easing: 'ease-in',
            fill: 'none'
        }
    ).onfinish = () => {
        overlay.style.clipPath = 'circle(200% at 100% 0%)';
        rootElement.dataset.theme = rootElement.dataset.theme != 'dark' ? 'dark' : 'light';
        overlay.animate(
            [
                { opacity: 1 },
                { opacity: 0 }
            ],
            {
                duration: 300,
                easing: 'ease-in',
                fill: 'none'
            }
        ).onfinish = () => {
            overlay.style.clipPath = 'circle(0% at 100% 0%)';
            overlay.style.backgroundColor = '';
            swappingTheme = false;

            document.cookie = `theme=${rootElement.dataset.theme};path=/;max-age=31536000`; // Update cookie
        };
    };
});