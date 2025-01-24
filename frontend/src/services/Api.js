// src/services/api.js
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000' // замените на URL вашего backend API

export const getRawData = (start_date, end_date) => {
    return axios.get(`${API_BASE_URL}/get_raw_data`, {
        params: {
            start_date,
            end_date,
        },
    })
}

export const downloadExcel = (start_date, end_date) => {
    return axios.get(`${API_BASE_URL}/download_excel`, {
        params: {
            start_date,
            end_date,
        },
        responseType: 'blob', // для загрузки Excel файла
    })
}
