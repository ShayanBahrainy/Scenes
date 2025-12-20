window.addEventListener('DOMContentLoaded', function () {
    console.log("window event added")
    const deleteButtons = document.querySelectorAll('.delete-button');
    deleteButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            const videoName = this.getAttribute('data-video-name');
            const confirmed = confirm("Are you sure you want to delete draft '" + videoName + "' ?");
            if (confirmed) {
                fetch('/admin/drafts/?video_name=' + encodeURIComponent(videoName), {
                    method: 'DELETE'
                })
            }
        })
    })

    const publishButtons = this.document.querySelectorAll('.publish-button');
    publishButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            const videoName = this.getAttribute('data-video-name');
            const confirmed = confirm("Are you sure you want to publish draft '" + videoName + "' ?");
            if (confirmed) {
                fetch('/admin/drafts/?video_name=' + encodeURIComponent(videoName), {
                    method: 'PUT'
                })
            }
        })
    })

    const backButton = this.document.querySelector('.back-button');
    backButton.addEventListener('click', function () {
        console.log("back click")
        window.location = '/admin/dashboard/';
    })
})
console.log('test123')