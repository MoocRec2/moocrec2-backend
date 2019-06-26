var express = require('express');
var router = express.Router();

/* GET home page. */
router.get('/', function(req, res, next) {
  //res.sendFile('/public/WEB/mainPage.html');

  res.send('<script> window.location.href = "mainPage.html"; </script>');
});

module.exports = router;
