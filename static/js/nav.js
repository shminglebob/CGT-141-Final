const btn = document.getElementById("navToggle");
const nav = document.querySelector(".nav-links");

btn.addEventListener("click", () => {
    btn.classList.toggle("active");
    nav.classList.toggle("open");
});
