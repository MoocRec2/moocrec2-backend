var express = require('express');
var router = express.Router();

/* GET users listing. */
router.get('/', function(req, res, next) {
  res.send('respond with a resource');
});

// Login Endpoint
router.post('/login', (req, res) => {
  if (req.body.username === undefined || req.body.username === null ||
    req.body.password === undefined || req.body.password === null) {
    res.status(400).send({ message: 'Bad Request' })
    return
  }

  // Perform authentication
  if (req.body.username === 'admin' && req.body.password === 'admin') {
    res.status(200).send({ message: 'Logged in Successfully' })
    return
  }

  res.status(403).send({ message: 'Incorrect Credentials' })

})

module.exports = router;
