const EDITOR_ID = "email-editor";

async function loadEmail(id) {
    const editor = document.getElementById(EDITOR_ID)
    if (editor.getAttribute('data-email-id') == id){
        return;
    }

    editor.setAttribute("data-email-id", id)

    const response = await fetch("/admin/email/edit/" + id)
    const data = await response.json()

    const email = data["emails"][0]

    let titleField = document.querySelector(".title-input")
    let bodyField = document.querySelector(".body-input")

    titleField.value = email["title"]
    bodyField.value = email["body"]
}

function toggleEditorVisibility() {
    let editor = document.getElementById("email-editor")

    editor.classList.toggle("email-editor-disabled")
    editor.classList.toggle("email-editor-enabled")
}

function getEditorVisibility() {
    let editor = document.getElementById(EDITOR_ID)

    return editor.classList.contains("email-editor-enabled")
}

async function save() {
    const editor = document.getElementById(EDITOR_ID)

    let data = {
        "title" : document.querySelector(".title-input").value,
        "body" : document.querySelector(".body-input").value
    }

    const email_id = editor.getAttribute("data-email-id")

    await fetch("/admin/email/edit/" + email_id, {
        method: "POST",
        body: JSON.stringify(data),
        headers: new Headers({'content-type': 'application/json'})
    })

    toggleEditorVisibility()
    location = location
}

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
        self.addEventListener("click", async function () {
            const id = self.getAttribute("data-email-id")

            let editor = document.getElementById(EDITOR_ID)

            const currentId = editor.getAttribute("data-email-id")

            if (!getEditorVisibility() || currentId == id) {
                toggleEditorVisibility()
            }

            if (id != currentId) {
                loadEmail(id)
            }

        })
    })

    const saveButton = this.document.querySelector(".save-button")
    saveButton.addEventListener("click", save)
})