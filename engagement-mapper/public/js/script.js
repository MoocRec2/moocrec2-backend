var myRecord = new viewRec();
myRecord.startRecord();
console.log("Activity recording started");

var ACTIVITY = [];
var FEEDBACK = [];
var video;
var videos = ["testVideo1.mp4", "testVideo2.mp4", "testVideo3.mp4", "testVideo4.mp4", "testVideo5.mp4"];
var sessionEnded = false;
var q1Rating = 0;
var q2Rating = 0;
var yetToInteractWithVideo = true;

function getIndexOfVideo(path) {
    for (var i = 0; i < videos.length; i++) {
        if (path.includes(videos[i])) {
            return i;
        }
    }

    return -1;
}

function findVidePreference() {
    var sessionData = JSON.parse(localStorage.getItem("training-session"));

    axios.post('http://localhost:3000/engagement/activity', sessionData)
        .then(function (response) {
            console.log(response);
        })
        .catch(function (error) {
            console.log(error);
        });
}


$(document).click(function (event) {
    // Capture clicked element.
    var element = event['target'];
    var elementId = element.id;
    var elementRole = element.getAttribute('role');

    // Capture status.
    var videoSegment = video.src;
    var time = video.currentTime;
    var position = getIndexOfVideo(videoSegment);


    // Validate.
    roles = ['playerControl', 'seekControl', 'playbackControl', 'previousSegment', 'nextSegment', 'fullScreen', 'volumeControl', 'playlist', 'mute'];
    if (roles.includes(elementRole)) {
        // when next | previous segment buttons are clicked, the function returns
        // the video that the user skipped to instead of the video that was playing,
        // when the user clicked the skip button.
        if (elementRole == 'previousSegment' && position < videos.length - 1) {
            videoSegment = videoSegment.replace(videos[position], videos[position + 1]);
        }
        else if (elementRole == 'nextSegment' && position >= 1) {
            videoSegment = videoSegment.replace(videos[position], videos[position - 1]);
        }

        ACTIVITY.push({
            ElementId: elementId,
            ElementRole: elementRole,
            VideoSegment: videoSegment,
            TimeAtVideoSegment: time
        });
    }

});

$(document).ready(function () {
    $("button img video div span").on("click", function () {
        // Known roles:-
        // playerControl | volumeControl | playlist | player
        var currentVideo = video.src;
        var currentTimeOfCurrentVideo = video.currentTime;
        var elementId = this.id;
        var elementRole = $(video).attr('role');

        var clickMetadata = {
            Segment: currentVideo,
            Time: currentTimeOfCurrentVideo,
            ElementId: elementId,
            elementRole: elementRole
        };
        console.log(this);
        ACTIVITY.push(clickMetadata);
    });

    $(".videoPlayer").toArray().forEach(function (videoPlayer) {
        // Video elemens.

        video = $(videoPlayer).find("video")[0];
        var playPauseBtn = $(videoPlayer).find(".playPausebtn");
        var fullscreen = $(videoPlayer).find(".fullscreen");
        var startTime = $(videoPlayer).find(".startTime");
        var endTime = $(videoPlayer).find(".endTime");
        var playerSeekBar = $(videoPlayer).find(".topControls .seekbar");
        var playerProgressBar = $(videoPlayer).find(".topControls .seekbar .progressbar");
        var volumeSeekBar = $(videoPlayer).find(".volumeCtrl .seekbar");
        var volumeProgressBar = $(videoPlayer).find(".volumeCtrl .seekbar .progressbar");
        var fastForward = $(videoPlayer).find(".forward");
        var fastBackward = $(videoPlayer).find(".backward");
        var volumePercentage = $(videoPlayer).find(".volumeCtrl .percentage");
        var playListItem = $(".playlistItem");
        var speakerIcon = $(videoPlayer).find(".loudSpeaker-icon");
        var ratingPopup = $("#popUpModal");

        var curDuration,
            endDuration,
            seekBarPercentage,
            interval,
            completeDuration;

        $(playPauseBtn).on("click", function () {
            completeDuration = video.duration;
            endDuration = calcDuration(completeDuration);

            endTime.text(
                `${endDuration.hours}:${endDuration.minutes}:${endDuration.seconds}`
            );

            // This function makes the video play.
            if (playPauseBtn.hasClass("play")) {
                video.play();
                playPauseBtn.addClass("pause").removeClass("play");
                $(videoPlayer).addClass("isPlaying");
            } else if (playPauseBtn.hasClass("pause")) {
                video.pause();
                playPauseBtn.addClass("play").removeClass("pause");
                $(videoPlayer).removeClass("isPlaying");
            }

            // Updating seekbar.
            interval = setInterval(function () {
                if (!video.paused) {
                    updateSeekbar();
                }
                if (video.paused) {
                    clearInterval(interval);
                }
                if (video.ended) {
                    clearInterval(interval);
                    $(playerProgressBar).css("width", "100%");
                    playPauseBtn.removeClass("pause").addClass("play");
                    $(videoPlayer).removeClass("isPlaying").addClass("showControls");
                }
            }, 500);
        });
        /* End play_pause on click */

        // FastBackwards function.
        fastBackward.on("click", function () {
            $("#popUpModal").modal("show");
            rateQuestion1();
            rateQuestion2();
            /*
            if (!video.ended && completeDuration != undefined) {
                video.currentTime > 0 && video.currentTime < video.duration ? (video.currentTime -= 10) : 0;
            }
            */

            /*
            var currentSrc = video.currentSrc;
            var filename;
            if (currentSrc) {
                var startIndex = (currentSrc.indexOf('\\') >= 0 ? currentSrc.lastIndexOf('\\') : currentSrc.lastIndexOf('/'));
                filename = currentSrc.substring(startIndex);
                if (filename.indexOf('\\') === 0 || filename.indexOf('/') === 0) {
                    filename = filename.substring(1);
                }
            }

            for (var i = 0; i < videos.length; i++) {
                if (filename == videos[i]) {
                    //console.log(videos[i+1]);
                    $(video).attr("src", videos[i - 1]);
                    //video.src = videos[i+1];
                    //console.log(filename, videos[i]);
                    // This function makes the video play.

                    //video.play();
                    function fix(video) {
                        var thePromise = video.play();

                        if (thePromise != undefined) {

                            thePromise.then(function (_) {

                                video.pause();
                                video.currentTime = 0;

                            });

                        }
                    }
                    playPauseBtn.addClass("pause").removeClass("play");
                    $(videoPlayer).addClass("isPlaying");
                    endDuration = calcDuration(completeDuration);

                    endTime.text(
                        `${endDuration.hours}:${endDuration.minutes}:${endDuration.seconds}`
                    );
                    // Updating seekbar.
                    interval = setInterval(function () {
                        if (!video.paused) {
                            updateSeekbar();
                        }
                        if (video.paused) {
                            clearInterval(interval);
                        }
                        if (video.ended) {
                            clearInterval(interval);
                            $(playerProgressBar).css("width", "100%");
                            playPauseBtn.removeClass("pause").addClass("play");
                            $(videoPlayer).removeClass("isPlaying").addClass("showControls");
                        }
                    }, 500);
                }
            }
            */
        });

        // FastForward function.
        fastForward.on("click", function () {
            /*
            if (!video.ended && completeDuration != undefined) {
                video.currentTime > 0 && video.currentTime < video.duration ? (video.currentTime += 10) : 0;
            }
            */
            /*
             if (!video.ended && completeDuration != undefined) {
                 video.currentTime > 0 && video.currentTime < video.duration ? (video.currentTime -= 10) : 0;
             }
             */
            $("#popUpModal").modal("show");
            rateQuestion1();
            rateQuestion2();


            var currentSrc = video.currentSrc;
            var filename;
            if (currentSrc) {
                var startIndex = (currentSrc.indexOf('\\') >= 0 ? currentSrc.lastIndexOf('\\') : currentSrc.lastIndexOf('/'));
                filename = currentSrc.substring(startIndex);
                if (filename.indexOf('\\') === 0 || filename.indexOf('/') === 0) {
                    filename = filename.substring(1);
                }
            }

            for (var i = 0; i < videos.length; i++) {
                if (filename == videos[i]) {

                    // Stop if the vide is at the end of the list.
                    if (i == video.length - 1) {
                        console.log('stopped')
                    }
                    else {
                        //console.log(videos[i+1]);
                        $(video).attr("src", videos[i + 1]);
                        //video.src = videos[i+1];
                        //console.log(filename, videos[i]);
                        // This function makes the video play.

                        /*video.play();
                        function fix(video) {
                            var thePromise = video.play();

                            if (thePromise != undefined) {

                                thePromise.then(function (_) {

                                    video.pause();
                                    video.currentTime = 0;

                                });

                            }
                        }*/
                        
                        playPauseBtn.addClass("pause").removeClass("play");
                        $(videoPlayer).addClass("isPlaying");
                        endDuration = calcDuration(completeDuration);

                        endTime.text(
                            `${endDuration.hours}:${endDuration.minutes}:${endDuration.seconds}`
                        );
                        // Updating seekbar.
                        interval = setInterval(function () {
                            if (!video.paused) {
                                updateSeekbar();
                            }
                            if (video.paused) {
                                clearInterval(interval);
                            }
                            if (video.ended) {
                                clearInterval(interval);
                                $(playerProgressBar).css("width", "100%");
                                playPauseBtn.removeClass("pause").addClass("play");
                                $(videoPlayer).removeClass("isPlaying").addClass("showControls");
                            }
                        }, 500);
                    }
                }
            }

        });

        // Change video location on seekbar onclick.
        playerSeekBar.on("click", function (e) {
            if (!video.ended && completeDuration != undefined) {
                var seekPosition = e.pageX - $(playerSeekBar).offset().left;
                if (
                    seekPosition >= 0 &&
                    seekPosition < $(playerSeekBar).outerWidth()
                ) {
                    video.currentTime =
                        (seekPosition * completeDuration) / $(playerSeekBar).outerWidth();
                    updateSeekbar();
                }
            }
        });

        // Update volume percentage.
        volumeSeekBar.on("click", function (e) {
            var volPosition = e.pageX - $(volumeSeekBar).offset().left;
            var videoVolume = volPosition / $(volumeSeekBar).outerWidth();

            if (videoVolume >= 0 && videoVolume <= 1) {
                video.volume = videoVolume;
                volumeProgressBar.css("width", videoVolume * 100 + "%");
                volumePercentage.text(Math.floor(videoVolume * 100) + "%");
            }
        });

        // Full screen.
        fullscreen.on("click", function () {
            if (video.requestFullscreen) {
                video.requestFullscreen();
            } else if (video.mozRequestFullScreen) {
                /* Firefox */
                video.mozRequestFullScreen();
            } else if (video.webkitRequestFullscreen) {
                /* Chrome, Safari and Opera */
                video.webkitRequestFullscreen();
            } else if (video.msRequestFullscreen) {
                /* IE/Edge */
                video.msRequestFullscreen();
            }
        });

        // Mute button.

        $(speakerIcon).on("click", function () {
            video.muted = true;
            speakerIcon.addClass("fas fa-volume-mute").removeClass("fa fa-volume-up");
        });

        // $(speakerIcon).on("click", function () {
        //     if (speakerIcon.hasClass("up")) {
        //         video.muted = true;
        //         speakerIcon.addClass("mute").removeClass("up");
        //     }
        //     else if (speakerIcon.hasClass("mute")) {
        //         video.muted = false;
        //         speakerIcon.addClass("up").removeClass("mute");
        //     }
        // });


        // Playlist controls.
        playListItem.on("click", function () {
            var videoSource = $(this).attr('source'); // testVideo1.mp4
            $(video).attr("src", videoSource);


            // This function makes the video play.
            video.play();
            playPauseBtn.addClass("pause").removeClass("play");
            $(videoPlayer).addClass("isPlaying");

            var curSrc = videoPlayer.currentSrc;

            video.addEventListener('loadedmetadata', function () {
                completeDuration = video.duration;
                console.log('Duration change', completeDuration);
            });

            // console.log("video complete duration" + completeDuration);
            endDuration = calcDuration(completeDuration);

            endTime.text(
                `${endDuration.hours}:${endDuration.minutes}:${endDuration.seconds}`
            );
            // Updating seekbar.
            interval = setInterval(function () {
                if (!video.paused) {
                    updateSeekbar();
                }
                if (video.paused) {
                    clearInterval(interval);
                }
                if (video.ended) {
                    clearInterval(interval);
                    $(playerProgressBar).css("width", "100%");
                    playPauseBtn.removeClass("pause").addClass("play");
                    $(videoPlayer).removeClass("isPlaying").addClass("showControls");
                }
            }, 500);

        });

        $("#submitFeedbackBtn").on("click", function () {
            var videoSegment = video.src;
            var position = getIndexOfVideo(videoSegment);   // starts from 0.
            var videoCount = videos.length; // starts from 1, like everything else :P

            // If this isn't the last video, take feedback, and go to next video.
            if (position != videoCount - 1) {
                FEEDBACK.push({
                    VideoSegment: videoSegment,
                    QuestionOneRating: q1Rating,
                    QuestionTwoRating: q2Rating
                });

                $("#closeFeedbackBtn").click();

                // move to next video.
                videoSegment = videoSegment.replace(videos[position], videos[position + 1]);
                video.src = videoSegment;
            }
            else {
                // Take feedback and submit everything.
                FEEDBACK.push({
                    VideoSegment: videoSegment,
                    QuestionOneRating: q1Rating,
                    QuestionTwoRating: q2Rating
                });

                $("#closeFeedbackBtn").click();

                localStorage.setItem("training-session", JSON.stringify({ Activity: ACTIVITY, Feedback: FEEDBACK }));
                window.location.href = "preference.html";
            }
        });

        // Toggle controls.
        $(videoPlayer).hover(
            function () {
                if ($(videoPlayer).hasClass("isPlaying")) {
                    $(videoPlayer).addClass("showControls");
                }
            },
            function () {
                setTimeout(function () {
                    if ($(videoPlayer).hasClass("isPlaying")) {
                        $(videoPlayer).removeClass("showControls");
                    }
                }, 2000);
            }
        );

        // When feedback form is closed.
        $('#closeFeedbackBtn').on('click', function () {
        });


        // Seekbar functionality updates go here.
        var updateSeekbar = function () {
            seekBarPercentage = getPercentage(video.currentTime, video.duration);
            curDuration = calcDuration(video.currentTime);
            startTime.text(
                `${curDuration.hours}:${curDuration.minutes}:${curDuration.seconds}`
            );
            $(playerProgressBar).css("width", seekBarPercentage + "%")
        };


        /* End foreach */
    });

    // Rating bar implementation.
    function rateQuestion1() {
        $('.ques1').starrr({
            change: function (e, value) {
                //alert('new rating is ' + value);
                document.getElementById("para").innerHTML = "You rated " + value + " !";
                q1Rating = value;
            }
        });
    }

    function rateQuestion2() {
        $('.ques2').starrr({
            change: function (e, value) {
                //alert('new rating is ' + value);
                document.getElementById("para2").innerHTML = "You rated " + value + " !";
                q2Rating = value;
            }
        });
    }

    // Display rating popup on video end.
    video.onended = function () {
        console.log("The video has ended");

        $("#popUpModal").modal("show");
        rateQuestion1();
        rateQuestion2();
    };

    $(".primary").on("click", function () {
        $(".ques1").starrr("option", "rating", "0");
    });



    /********** Other funcions ************/
    // This function calculates the volume percentage.
    var getPercentage = function (presentTime, totalLength) {
        var calculatePercentage = (presentTime / totalLength) * 100;
        return parseFloat(calculatePercentage.toString());
    };

    // This function calculates the duration of video.
    var calcDuration = function (duration) {
        var seconds = parseInt(duration % 60);
        var minutes = parseInt((duration % 3600) / 60);
        var hours = parseInt(duration / 3600);

        return {
            hours: pad(hours),
            minutes: pad(minutes.toFixed()),
            seconds: pad(seconds.toFixed())
        };
    };

    var pad = function (number) {
        if (number > -10 && number < 10) {
            return "0" + number;
        } else {
            return number;
        }
    };

    /* End main */
});


