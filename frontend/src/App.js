// src/App.js
import React, { useState } from 'react'
import DatePickerComponent from './components/DatePicker'
import { getRawData, downloadExcel } from './services/Api'
import './App.css'

const App = () => {
    const [startDate, setStartDate] = useState(null)
    const [endDate, setEndDate] = useState(null)
    const [error, setError] = useState('')
    const [data, setData] = useState([])
    const [loading, setLoading] = useState(false)

    // Проверка на корректность дат
    const handleStartDateChange = (date) => {
        setStartDate(date)
        if (endDate && date > endDate) {
            setError('Дата начала не может быть позже даты окончания')
        } else {
            setError('')
        }
    }

    const handleEndDateChange = (date) => {
        setEndDate(date)
        if (startDate && date < startDate) {
            setError('Дата окончания не может быть раньше даты начала')
        } else {
            setError('')
        }
    }

    const handleShowTable = async () => {
        setLoading(true)
        try {
            const response = await getRawData(
                startDate.toISOString().split('T')[0],
                endDate.toISOString().split('T')[0]
            )
            setData(response.data)
        } catch (err) {
            console.error('Ошибка при получении данных:', err)
        } finally {
            setLoading(false)
        }
    }

    const handleDownloadExcel = async () => {
        try {
            const response = await downloadExcel(
                startDate.toISOString().split('T')[0],
                endDate.toISOString().split('T')[0]
            )
            const file = new Blob([response.data], {
                type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            })
            const fileURL = URL.createObjectURL(file)
            const link = document.createElement('a')
            link.href = fileURL
            link.download = `data_${startDate.toISOString().split('T')[0]}_${
                endDate.toISOString().split('T')[0]
            }.xlsx`
            link.click()
        } catch (err) {
            console.error('Ошибка при загрузке файла:', err)
        }
    }

    const isDateRangeValid = startDate && endDate && !error
    const isLongRange = endDate && startDate && endDate - startDate > 30 * 24 * 60 * 60 * 1000 // больше месяца

    return (
        <div className='App'>
            <h1>Выберите даты для формирования отчёта</h1>
            <div className='input-container'>
                <div className={`date-picker-container ${error ? 'error' : ''}`}>
                    <label>Начало</label>
                    <DatePickerComponent
                        selectedDate={startDate}
                        onChange={handleStartDateChange}
                        maxDate={endDate}
                    />
                </div>
                <div className={`date-picker-container ${error ? 'error' : ''}`}>
                    <label>Окончание</label>
                    <DatePickerComponent
                        selectedDate={endDate}
                        onChange={handleEndDateChange}
                        minDate={startDate}
                    />
                </div>
            </div>

            {error && <p className='error-message'>{error}</p>}

            {isDateRangeValid && (
                <>
                    <div className='buttons'>
                        {!isLongRange && (
                            <button onClick={handleShowTable}>Показать таблицу</button>
                        )}
                        <button onClick={handleDownloadExcel}>Загрузить Excel</button>
                    </div>
                </>
            )}

            {loading && <p>Загрузка...</p>}
            {data.length > 0 && !loading && (
                <table>
                    <thead>
                        <tr>
                            {/* Генерация заголовков таблицы на основе ключей первого объекта */}
                            {data.length > 0 &&
                                Object.keys(data[0]).map((key, index) => (
                                    <th key={index}>{key}</th>
                                ))}
                        </tr>
                    </thead>
                    <tbody>
                        {/* Генерация строк таблицы */}
                        {data.map((row, rowIndex) => (
                            <tr key={rowIndex}>
                                {/* Генерация ячеек строки на основе значений объекта */}
                                {Object.values(row).map((value, cellIndex) => (
                                    <td key={cellIndex}>{value}</td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    )
}

export default App
