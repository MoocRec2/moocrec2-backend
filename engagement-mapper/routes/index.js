var express = require('express');
var router = express.Router();

/* GET home page. */
router.get('/', function(req, res, next) {
  //res.sendFile('/public/WEB/mainPage.html');

  res.sendFile('../public/WEB/mainPage.html', { root: __dirname });
});

module.exports = router;
