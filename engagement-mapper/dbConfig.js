var mongoose = require('mongoose')
var Schema = mongoose.Schema

var courseSchema = new Schema(
    {
        "_id": { type: String, required: true },
        "key": { type: String, required: false },
        "aggregation_key": { type: String, required: false },
        // "authoring_organization_uuids": [
        //     "518a47f2-66fb-4529-8902-a4f7ca3002ef"
        // ],
        "availability": { type: String, required: false },
        "content_type": { type: String, required: false },
        // "end": "2020-06-08T23:00:00Z",
        // "enrollment_end": null,
        // "enrollment_start": null,
        "first_enrollable_paid_seat_price": { type: Number, required: false },
        "first_enrollable_paid_seat_sku": { type: String, required: false },
        "full_description": { type: String, required: false },
        // "go_live_date": null,
        "has_enrollable_seats": { type: Boolean, required: false },
        "image_url": { type: String, required: false },
        "language": { type: String, required: false },
        "level_type": { type: String, required: false },
        // "logo_image_urls": [
        //     "https://www.edx.org/sites/default/files/school/image/logo/upv_200x101.jpg"
        // ],
        "marketing_url": { type: String, required: false },
        "max_effort": { type: Number, required: false },
        "min_effort": { type: Number, required: false },
        // "mobile_available": false,
        "number": { type: String, required: false },
        "org": { type: String, required: false },
        "pacing_type": { type: String, required: false },
        "partner": { type: String, required: false },
        // "program_types": [],
        // "published": true,
        // "seat_types": [
        //     "verified",
        //     "audit"
        // ],
        "short_description": { type: String, required: false },
        // "staff_uuids": [
        //     "8da4a544-bb49-4db4-9d49-20440809df8d",
        //     "93c3362d-f8b1-4c36-b74b-e1bdede46256"
        // ],
        "start": { type: String, required: false },
        // "subject_uuids": [
        //     "e52e2134-a4e4-4fcb-805f-cbef40812580"
        // ],
        "title": { type: String, required: false },
        // "transcript_languages": [
        //     "Spanish"
        // ],
        "type": { type: String, required: false },
        // "weeks_to_complete": 4,
        // "platform": 0
    }
)

mongoose.model('Course', courseSchema, '')

mongoose.connect('mongodb://api:backendapi1@ds157901.mlab.com:57901/moocrecv2', { useNewUrlParser: true }, error => {
    if (error) {
        console.error(error)
        process.exit(-1)
    }
    console.log("Connected to the DB");
})

module.exports = mongoose