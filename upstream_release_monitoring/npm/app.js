const ChangesStream = require('changes-stream');
const Request = require('request');
const Normalize = require('normalize-registry-metadata');
const fs = require('fs');
const db = 'https://replicate.npmjs.com';
const latest_fetched = "/tmp/latest_fetched_npm_package";
var changes = new ChangesStream({
  db: db,
  include_docs: true
});

var package_versions = {
    name: '',
    changed: ''
};

//Check if we have stored latest fetched change
//If true fetch from it till for ever
if (fs.existsSync(latest_fetched)) {
  fs.readFileSync(latest_fetched, 'utf8', function (err,data) {
    if (err) {
      return console.log(err);
    }
  console.log(data);});
}


Request.get(db, function(err, req, body) {
  var end_sequence = JSON.parse(body).update_seq;
  changes.on('data', function(change) {
    //if (change.seq >= end_sequence) {
    //  process.exit(0);
    //}

    if (change.doc.name) {
      normalized = Normalize(change.doc);
      package_versions['name'] = normalized.name;
      package_versions['changed'] = normalized.time;
      fs.writeFileSync(latest_fetched, JSON.stringify(package_versions), function(err) {
        if(err) {
          return console.log(err);
        }
      });
      console.log(package_versions);
    }
  });
});
