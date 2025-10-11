window.addEventListener("load", function () {
    const hamburger = document.querySelector(".hamburger");
    const menu = this.document.querySelector(".menu");
    hamburger.addEventListener("click", function () {
        hamburger.classList.toggle("opened-hamburger")
        hamburger.classList.toggle("closed-hamburger")
        menu.classList.toggle("menu-opened")
        menu.classList.toggle("menu-closed")
    });
})