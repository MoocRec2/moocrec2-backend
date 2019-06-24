var express = require('express');
var router = express.Router();

/* GET home page. */
router.get('/', function(req, res, next) {
  res.send({Message: 'Engagement'});
});

// Receive all activity data from the UI.
router.post('/activity', function(req, res, next) {
    var allVideos = ["testVideo1.mp4", "testVideo2.mp4", "testVideo3.mp4", "testVideo4.mp4", "testVideo5.mp4"];
    var activities = req.body.Activity;
    var feedbacks = req.body.Feedback;
    var segmentLength = 3600; // miliseconds.

    var skippedSegments = [];
    var unskipped = [];
    var mutedSegments = [];
    var easinessToUnderstand = [];
    var interestingToWatch = [];
    var watchedScore = {};

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


    // Analyze activity.
    activities.forEach(activity => {
        var videoSegment = activity['VideoSegment'];

        // Score skipped segmetns.
        if (activity['ElementRole'] == 'nextSegment' || activity['ElementRole'] == 'previousSegment') {
            skippedSegments.push(activity['VideoSegment']);

            // Highest duration of the segment watched is found out in case,
            // the user watched the same segment more than once.
            if (!watchedScore.hasOwnProperty('TimeAtVideoSegment')) {
                watchedScore[videoSegment] = (activity['TimeAtVideoSegment'] / segmentLength) * 100;  // 100%.
            }
            else {
                var score = (activity['TimeAtVideoSegment'] / segmentLength) * 100;
                if (score > watchedScore[videoSegment]) {
                    watchedScore[videoSegment] = score;
                }
            }
        }

        // Noting down muted segments.
        else if (activity['ElementRole'] == 'mute') {
            mutedSegments.push(activity['VideoSegment']);
        }
    });

    // Fully watched segments.
    for (var i = 0; i < allVideos.length; i++) {
        var commonElement = false;
        for (var k = 0; k < skippedSegments.length; k++) {
            if (skippedSegments[k] == allVideos[i]) {
                commonElement = true;
                break;
            }
        }

        if (commonElement) {
            unskipped.push(allVideos[i]);
        }
    }
  
    // Analyze feedback.
    easinessToUnderstand = feedbacks.sort(function(a, b) {
        return b.QuestionOneRating > a.QuestionOneRating ? 1 : b.QuestionOneRating < a.QuestionOneRating ? -1 : 0;
    });

    interestingToWatch = feedbacks.sort(function(a, b) {
        return b.QuestionTwoRating > a.QuestionTwoRating ? 1 : b.QuestionTwoRating < a.QuestionTwoRating ? -1 : 0;
    });

    console.log(req.body);
    console.log('\n\n');
    console.log(skippedSegments);
    console.log(unskipped);
    console.log(mutedSegments);
    console.log(easinessToUnderstand);
    console.log(interestingToWatch);
    console.log(watchedScore);

    res.send({});
});

module.exports = router;
