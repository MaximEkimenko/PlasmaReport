// App.js
import React, { useEffect, useState } from 'react'
import { DataGrid, GridToolbar } from '@mui/x-data-grid'
import {
    Box,
    TextField,
    Button,
    Paper,
    Typography,
    Tooltip,
    ThemeProvider,
    createTheme,
} from '@mui/material'
import SearchIcon from '@mui/icons-material/Search' // Иконка поиска
import SendIcon from '@mui/icons-material/Send' // Иконка отправки
import FileDownloadIcon from '@mui/icons-material/FileDownload' // Иконка экспорта
import * as XLSX from 'xlsx'

// Создаем кастомную тему Material-UI
const theme = createTheme({
    palette: {
        primary: {
            main: '#1976d2', // Синий цвет
        },
        secondary: {
            main: '#f50057', // Розовый цвет
        },
    },
    typography: {
        fontFamily: 'Arial, sans-serif',
    },
})

function App() {
    const [data, setData] = useState([]) // Все данные таблицы
    const [pageSize, setPageSize] = useState(50)
    const [searchTerm, setSearchTerm] = useState('')
    const [selectedRows, setSelectedRows] = useState([]) // Выбранные строки

    // Загрузка данных с сервера
    useEffect(() => {
        fetch('http://192.168.8.163:8000/master/get_programs_for_assignment')
            .then((response) => response.json())
            .then((json) => setData(json))
            .catch((error) => console.error('Error fetching data:', error))
    }, [])

    // Фильтрация данных
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
        const flatKeys = flattenObjectKeys(firstRow)
        return [
            ...flatKeys.map((key) => ({
                field: key,
                headerName:
                    key.split('.').pop().charAt(0).toUpperCase() + key.split('.').pop().slice(1),
                width: 200,
                editable: true,
            })),
        ]
    }, [data])

    // Обработка обновления строки
    const handleProcessRowUpdate = (newRow, oldRow) => {
        const updatedData = data.map((row) => (row.id === newRow.id ? newRow : row))
        setData(updatedData) // Обновляем состояние с новыми данными
        return newRow // Возвращаем обновленную строку
    }

    // Отправка выбранных ID и обновленных данных на сервер
    const handleSendSelectedIds = () => {
        const selectedIds = selectedRows

        // Находим обновленные данные для выбранных строк
        const updatedData = data.filter((row) => selectedIds.includes(row.id))

        console.log('Sending updated data to server:', updatedData)

        // Отправляем данные на сервер
        fetch('/api/send-ids', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ids: selectedIds, updatedData }),
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
        <ThemeProvider theme={theme}>
            <Box sx={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
                {/* Заголовок */}
                <Typography
                    variant='h4'
                    gutterBottom
                    sx={{ color: 'primary.main', fontWeight: 'bold' }}
                >
                    MUI X DataGrid Example
                </Typography>

                {/* Блок поиска и кнопок */}
                <Paper elevation={3} sx={{ padding: '20px', marginBottom: '20px' }}>
                    <Typography variant='h6' gutterBottom>
                        Управление данными
                    </Typography>
                    <Box
                        sx={{
                            display: 'flex',
                            gap: '10px',
                            alignItems: 'center',
                            marginBottom: '10px',
                        }}
                    >
                        {/* Поле поиска */}
                        <TextField
                            label='Поиск'
                            variant='outlined'
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            fullWidth
                            InputProps={{
                                startAdornment: <SearchIcon sx={{ marginRight: '8px' }} />,
                            }}
                        />
                        {/* Кнопки */}
                        <Tooltip title='Отправить выбранные ID'>
                            <Button
                                variant='contained'
                                color='primary'
                                onClick={handleSendSelectedIds}
                                disabled={selectedRows.length === 0}
                                startIcon={<SendIcon />}
                            >
                                Отправить ({selectedRows.length})
                            </Button>
                        </Tooltip>
                        <Tooltip title='Экспорт в Excel'>
                            <Button
                                variant='contained'
                                color='secondary'
                                onClick={handleExportToExcel}
                                startIcon={<FileDownloadIcon />}
                            >
                                Экспорт
                            </Button>
                        </Tooltip>
                    </Box>
                </Paper>

                {/* Таблица */}
                <Paper elevation={3} sx={{ height: 600, width: '100%', padding: '20px' }}>
                    <DataGrid
                        rows={filteredData}
                        columns={columns}
                        pageSize={pageSize}
                        onPageSizeChange={(newPageSize) => setPageSize(newPageSize)}
                        rowsPerPageOptions={[10, 50, 100]}
                        pagination
                        checkboxSelection
                        disableSelectionOnClick
                        onRowSelectionModelChange={(newSelection) => {
                            setSelectedRows(newSelection) // Обновляем выбранные строки
                        }}
                        experimentalFeatures={{
                            columnReorder: true,
                            newEditingApi: true,
                        }}
                        processRowUpdate={handleProcessRowUpdate} // Обработка обновления строки
                        components={{
                            Toolbar: GridToolbar,
                        }}
                        sx={{
                            '& .MuiDataGrid-cell:hover': {
                                backgroundColor: 'rgba(0, 255, 0, 0.2)', // Эффект наведения
                            },
                        }}
                    />
                </Paper>
            </Box>
        </ThemeProvider>
    )
}

// Рекурсивная функция для получения всех ключей
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
