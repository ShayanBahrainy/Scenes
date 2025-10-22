window.addEventListener("DOMContentLoaded", function () {
    const createNewButton = this.document.querySelector(".create-new")
    createNewButton.addEventListener("click", function () {
        location = "/admin/email/new"
    })

    const sendButtons = this.document.querySelectorAll(".send-button")
    sendButtons.forEach(function (self) {
        self.addEventListener("click", function () {
            const id = self.getAttribute("data-email-id")
            fetch("/admin/email/send", {
                method: "POST",
                data: JSON.stringify({email_id:id})
            })
        })
    })

    const editButtons = this.document.querySelectorAll(".edit-button")
    editButtons.forEach(function (self) {
        self.addEventListener("click", function () {
            const id = self.getAttribute("data-email-id")
            location = "/admin/email/edit/" + id
        })
    })
})