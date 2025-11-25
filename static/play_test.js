function createVideoPlayer() {
    const video = document.createElement("video")
    video.classList = "fade-in video-player"
    video.autoplay = true

    return video
}

function playSegment(videoPlayer, segmentIndex) {

    let resolveOuter
    function saveResolve(resolve) {
        resolveOuter = resolve
    }
    let promise = new Promise(saveResolve)

    let mediaSource = new MediaSource()

    videoPlayer.src = URL.createObjectURL(mediaSource)

    mediaSource.addEventListener("sourceopen", () => {
        const videoBuffer = mediaSource.addSourceBuffer('video/webm codecs="vp9"')
        const audioBuffer = mediaSource.addSourceBuffer('audio/webm codecs="vorbis')

        Promise.all([
            fetch(`/video_4_seg${segmentIndex}.webm`).then(r => r.arrayBuffer()),
            fetch(`/audio_seg${segmentIndex}.webm`).then(r => r.arrayBuffer())
        ]).then(([videoData, audioData]) => {
            videoBuffer.appendBuffer(videoData)
            audioBuffer.appendBuffer(audioData)
            videoBuffer.addEventListener("updateend", function a() {

                resolveOuter(mediaSource)

                videoBuffer.removeEventListener("updateend", a)
            })
        }).catch(err => {
                console.error("Failed to fetch segment", segmentIndex, err)
        })
    })
    return promise
}

window.addEventListener("load", function () {
    let segmentIndex = 0

    let prev = null
    async function createTransition() {
        let video = createVideoPlayer()
        this.document.body.appendChild(video)
        let mediaSource = await playSegment(video, segmentIndex)
        segmentIndex++
        if (prev) {
            prev.classList.toggle('fade-in')
            prev.classList.toggle('fade-out')
            prev.muted = true
            let toDelete = prev
            setTimeout(() => {
                toDelete.src = ""
                toDelete.remove()
            }, 1000)
        }
        prev = video
        setTimeout(createTransition, (mediaSource.duration * 1000) - 1000)
    }

    createTransition()



})
