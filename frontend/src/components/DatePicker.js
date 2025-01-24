// src/components/DatePicker.js
import React from 'react'
import DatePicker from 'react-datepicker'
import 'react-datepicker/dist/react-datepicker.css'

const DatePickerComponent = ({ selectedDate, onChange, minDate, maxDate }) => {
    return (
        <DatePicker
            selected={selectedDate}
            onChange={onChange}
            minDate={minDate}
            maxDate={maxDate}
            dateFormat='yyyy-MM-dd'
            className='date-picker'
        />
    )
}

export default DatePickerComponent
