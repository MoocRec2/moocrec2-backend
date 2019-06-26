var express = require('express');
var router = express.Router();

/* GET home page. */
router.get('/', function(req, res, next) {
  res.send({Message: 'Engagement'});
});

// Receive all activity data from the UI.
router.post('/activity', function(req, res, next) {
    var allVideos = ["testVideo1.mp4", "testVideo2.mp4", "testVideo3.mp4"];
    var activities = req.body.Activity;
    var feedbacks = req.body.Feedback;
    var segmentLength = 3600; // miliseconds.

    // Get rid of full video path.
    for (var i = 0; i < activities.length; i++) {
        var path = activities[i]['VideoSegment'];
        path = path.substring(path.lastIndexOf('/') + 1);
        activities[i]['VideoSegment'] = path;
    }
    // Get rid of full video path.
    for (var i = 0; i < feedbacks.length; i++) {
        var path = feedbacks[i]['VideoSegment'];
        path = path.substring(path.lastIndexOf('/') + 1);
        feedbacks[i]['VideoSegment'] = path;
    } 

    /* Analyze user activity */

    // Sort based on at what time of each segment the actions were
    // performed.
    // maximize, skip, mute, replay, seek
    // if a video is not skipped, we consider the video was skipped after,
    // its full duration; for consistency.
    var activityScore = {
        'testVideo1.mp4': [0,segmentLength,0,0,0],
        'testVideo2.mp4': [0,segmentLength,0,0,0],
        'testVideo3.mp4': [0,segmentLength,0,0,0],
    };
    var skippedSegments = {};

    activities.forEach(activity => {
        var videoSegment = activity['VideoSegment'];
        var control = activity['ElementRole'];

        switch(control) {
            case 'fullScreen': activityScore[videoSegment][0] += 1; break;
            case 'mute': activityScore[videoSegment][2] += 1; break;
            case 'replayControl': activityScore[videoSegment][3] += 1; totalReplays += 1; break;
            case 'seekControl': activityScore[videoSegment][4] += 1; break;
            case 'nextSegment': 
                // If replayed segments are skipped, we might get multiple skipped actions
                // for same video.
                // In that case, only consider the occurance with highest watched-duration.
                if (!skippedSegments.hasOwnProperty(videoSegment)) { skippedSegments[videoSegment] = 0; };
                if (activity['TimeAtVideoSegment'] > skippedSegments[videoSegment]) {
                    skippedSegments[videoSegment] = activity['TimeAtVideoSegment'];
                }
                break;
            
            default: break;
        }
    });
    
    // Skipped segments.
    Object.keys(skippedSegments).forEach(videoSegment => {
        activityScore[videoSegment][1] = skippedSegments[videoSegment];
    });

    
    /* Analyze user feedback */
    // Get the average of the two questions' feedback.
    var feedbackScore = {};
    feedbacks.forEach(feedback => {
        var videoSegment = feedback['VideoSegment'];
        var q1 = feedback['QuestionOneRating'];
        var q2 = feedback['QuestionTwoRating'];

        feedbackScore[videoSegment] = (q1 + q2) / 2;
    });

    /* Analyze activity and feedback scores together. */
    var finalScore = {};
    allVideos.forEach(videoSegment => {
        finalScore[videoSegment] = 0;
        
        // considering activity score.
        // consider maximize, skip and replay actions.
        // order in array:- maximize, skip, mute, replay, seek
        if (activityScore[videoSegment][0] > 0) { finalScore[videoSegment] += 0.2; }    // maximize.
        if (activityScore[videoSegment][3] > 0) { finalScore[videoSegment] += 0.2; }    // replay.
        finalScore[videoSegment] += (activityScore[videoSegment][1] / segmentLength);     // skipped duration score.

        // considering feedback score average.
        finalScore[videoSegment] += feedbackScore[videoSegment];
    });

    // Highest score.
    var scoresArray = [];
    Object.keys(finalScore).forEach(key => {
        scoresArray.push({
            'VideoSegment': key,
            'Score': finalScore[key]
        });
    });
    
    // Highest scored video segment.
    var result = scoresArray.reduce((prev, current) => (prev.y > current.y) ? prev : current)

    res.send({'HighestScore': result, 'AllScores': finalScore});
});

module.exports = router;
