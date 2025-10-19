window.addEventListener('DOMContentLoaded', function () {
    const revertButtons = this.document.querySelectorAll('.revert-button');
    revertButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            const videoName = this.getAttribute('data-video-name');
            const confirmed = confirm("Are you sure you want to revert video '" + videoName + "' to a draft?");
            if (confirmed) {
                fetch('/admin/videos/?video_name=' + encodeURIComponent(videoName), {
                    method: 'PUT'
                })
            }
        })
    })

    const pageLinks = this.document.querySelectorAll('.page-link');
    pageLinks.forEach(function (link) {
        link.addEventListener('click', function (event) {
            const page = this.getAttribute('data-page');
            window.location = '/admin/published/?page=' + page;
        })
    })
})