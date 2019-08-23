var express = require('express');
var router = express.Router();
var mongoose = require('../dbConfig')
var courseModel = mongoose.model('Course')

/* GET users listing. */
router.get('/', function (req, res, next) {
    res.send('respond with a resource');
});

router.get('/top-rated', (req, res) => {
    courseModel.find({ score: { $exists: 1 } }).sort({ score: -1 }).limit(10).exec().then(documents => {
        res.status(200).send(documents)
    }, error => {
        console.error(error)
        res.status(500).send('Error')
    })
})

router.get('/search/:query', (req, res) => {
    var query = req.params.query
    console.log(query)
    courseModel.find({ title: { $regex: new RegExp(query), $options: 'i' } }).limit(10).exec().then(documents => {
        res.status(200).send(documents)
    }, error => {
        console.error(error)
        res.status(500).send('Error')
    })
})

module.exports = router;
