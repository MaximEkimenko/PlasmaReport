// App.js
import React, { useEffect, useState } from 'react'
import { DataGrid, GridToolbar } from '@mui/x-data-grid'
import { Box, TextField, Button } from '@mui/material'
import * as XLSX from 'xlsx' // Библиотека для работы с Excel

function App() {
    const [data, setData] = useState([])
    const [pageSize, setPageSize] = useState(50) // Размер страницы
    const [searchTerm, setSearchTerm] = useState('') // Глобальный поиск
    const [selectedRows, setSelectedRows] = useState([]) // Выбранные строки

    // Загрузка данных с сервера
    useEffect(() => {
        fetch('http://192.168.8.163:8000/master/get_programs_for_assignment') // Ваш API
            .then((response) => response.json())
            .then((json) => setData(json))
            .catch((error) => console.error('Error fetching data:', error))
    }, [])

    // Функция для фильтрации данных
    const filteredData = React.useMemo(() => {
        if (!searchTerm) return data

        return data.filter((row) =>
            Object.values(row).some((value) =>
                String(value).toLowerCase().includes(searchTerm.toLowerCase())
            )
        )
    }, [data, searchTerm])

    // Определение колонок
    const columns = React.useMemo(() => {
        if (data.length === 0) return []

        const firstRow = data[0]
        const flatKeys = flattenObjectKeys(firstRow) // Рекурсивное получение всех ключей

        return [
            ...flatKeys.map((key) => ({
                field: key, // Ключ для доступа к данным
                headerName:
                    key.split('.').pop().charAt(0).toUpperCase() + key.split('.').pop().slice(1), // Заголовок
                width: 200,
                editable: true, // Разрешаем редактирование
            })),
        ]
    }, [data])

    // Обновление данных при редактировании
    const handleEditCellChange = (updatedRow) => {
        setData((prevData) => prevData.map((row) => (row.id === updatedRow.id ? updatedRow : row)))
    }

    // Отправка выбранных id на сервер
    const handleSendSelectedIds = () => {
        const selectedIds = selectedRows.map((row) => row.id)
        console.log('Sending selected IDs to server:', selectedIds)

        // Здесь можно добавить запрос на сервер, например:
        fetch('/api/send-ids', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ids: selectedIds }),
        })
            .then((response) => response.json())
            .then((result) => console.log('Server response:', result))
            .catch((error) => console.error('Error sending IDs:', error))
    }

    // Выгрузка данных в Excel
    const handleExportToExcel = () => {
        const worksheet = XLSX.utils.json_to_sheet(filteredData)
        const workbook = XLSX.utils.book_new()
        XLSX.utils.book_append_sheet(workbook, worksheet, 'Users')
        XLSX.writeFile(workbook, 'users.xlsx')
    }

    return (
        <Box sx={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
            <h1>MUI X DataGrid Example</h1>

            {/* Глобальный поиск */}
            <TextField
                label='Search'
                variant='outlined'
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                fullWidth
                sx={{ marginBottom: '20px' }}
            />

            {/* Кнопки */}
            <Box sx={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
                <Button
                    variant='contained'
                    color='primary'
                    onClick={handleSendSelectedIds}
                    disabled={selectedRows.length === 0}
                >
                    Send Selected IDs ({selectedRows.length})
                </Button>
                <Button variant='contained' color='secondary' onClick={handleExportToExcel}>
                    Export to Excel
                </Button>
            </Box>

            {/* Таблица */}
            <div style={{ height: 600, width: '100%' }}>
                <DataGrid
                    rows={filteredData}
                    columns={columns}
                    pageSize={pageSize}
                    onPageSizeChange={(newPageSize) => setPageSize(newPageSize)}
                    rowsPerPageOptions={[10, 50, 100]} // Варианты размера страницы
                    pagination
                    checkboxSelection // Включаем выбор строк
                    // disableSelectionOnClick // Отключаем выбор строк по клику
                    onSelectionModelChange={(newSelection) => {
                        console.log('New Selection:', newSelection) // Для отладки
                        const selectedIDs = new Set(newSelection)
                        const selectedData = filteredData.filter((row) => selectedIDs.has(row.id))
                        setSelectedRows(selectedData)
                    }}
                    experimentalFeatures={{
                        columnReorder: true, // Включаем перемещение колонок
                        newEditingApi: true, // Включаем новую систему редактирования
                    }}
                    onCellEditCommit={handleEditCellChange} // Обработка редактирования ячеек
                    components={{
                        Toolbar: GridToolbar, // Добавляем панель инструментов для экспорта и других функций
                    }}
                />
            </div>
        </Box>
    )
}

// Рекурсивная функция для получения всех ключей (включая вложенные)
function flattenObjectKeys(obj, parentKey = '', keys = []) {
    for (const key in obj) {
        if (typeof obj[key] === 'object' && obj[key] !== null) {
            flattenObjectKeys(obj[key], `${parentKey}${key}.`, keys)
        } else {
            keys.push(`${parentKey}${key}`)
        }
    }
    return keys
}

export default App
