window.addEventListener("DOMContentLoaded", function () {
    this.document.querySelector(".file-upload-visual")?.addEventListener("click", function() {
        document.querySelector(".file-upload-real")?.click()
    })
})