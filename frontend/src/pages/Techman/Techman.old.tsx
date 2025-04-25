import React, { useState, useEffect, lazy, Suspense, useRef, ChangeEvent, useContext } from "react";

//import { useDispatch, useSelector } from "react-redux";
import { Link, useNavigate } from "react-router-dom";
import { Link as MuiLink } from "@mui/material";
import CustomToolbar from "../../components/CustomToolbar/CustomToolbar.tsx";

import { TechProgramType, ProcessedPrognameType, DateDiapazonType } from "./Techman.types.ts";
// import { AddDispatch, RootState } from "../../store/store";
// import { dateDiapazonActions } from "../../store/date_diapazon.slice";
// import { DateDiapazon } from "../../components/DateDiapazon/DateDiapazon";
import { DateDiapazon } from "../../components/DateDiapazon/DateDiapazon.tsx";
import Notification from "../../components/Notification/Notification.tsx";
import GlobalFilter from "../../components/GlobalFilter/GlobalFilter.tsx";
import { techmanCreateData, getNewPrograms } from "../../utils/requests.ts";
import { ICreateData } from "./Techman.types.ts";
import { Box, Typography, Button, Stack, Checkbox } from "@mui/material";
import { Select, MenuItem, FormControl, InputLabel, SelectChangeEvent } from "@mui/material";

import {
    DataGrid,
    GridColDef,
    GridColType,
    GridRenderCellParams,
    ValueOptions,
    GridToolbar,
    GridRowSelectionModel,
    GridSingleSelectColDef,
    useGridApiRef,
} from "@mui/x-data-grid";
import dayjs from "dayjs";
import { DateDiapazonContext } from "../../context.tsx";
import { endpoints } from "../../utils/authorization.ts";

type PrognameAndIdType = Exclude<TechProgramType, undefined> & { id: string; checked: boolean };

const blancOption = "---";

type ProgNameKeysType = keyof PrognameAndIdType;

// колонки, которые будут отображаться в таблице
const columnDict: Partial<{ [key in ProgNameKeysType]: string }> = {
    PostDateTime: "string",
    ProgramName: "string",
    program_status: "singleSelect",
    // UserName: "singleSelect",
    Material: "string",
};

// структура, формирующая опуии для авпадающих списков для полей типа "singleSelect"
type selecOptionsType = Partial<{ [key in ProgNameKeysType]: string[] }> | undefined;

/**
 * Сам компонент
 * @returns
 */
const Techman = () => {
    // интерфейс для управления таблицей
    const apiRef = useGridApiRef();
    // диапазон дат, за который будут загружаться данные
    const { dateDiapazon, setDateDiapazon } = useContext(DateDiapazonContext);
    //данные пришедшие из запроса в первоначальном виде
    const [rawData, setRawData] = useState<TechProgramType[]>([]);
    // данные, обработанные для отображения в таблице(все данные целиком, в том числе и те, которые не показываются)
    const [data, setData] = useState<ProcessedPrognameType[]>([]);
    // данные после фильтрации(именно они отбражаются в таблице)
    const [filteredData, setFilteredData] = useState<ProcessedPrognameType[]>([]);
    // количество программ, выделенных для загрузки в нашу таблицу из сигмы
    const [selectedPrograms, setSelectedPrograms] = useState<number>(0);
    // стабильная переменная для храенеия данных о столбцах таблицы]
    const columns = useRef<GridColDef[]>([]);
    // пользователи, хранимые в выпадающем списке для фильтрации
    const userOptions = useRef<selecOptionsType>(undefined);
    // список значений выставленных в выпадающих фильтрах, по которым фильтруется таблица
    const [filterValue, setFilterValue] = useState<Partial<Record<ProgNameKeysType, string>>>({});
    const [noData, setNoData] = useState(false);
    // объект русификации заголовков  таблицы
    const headers = useRef({});
    const navigate = useNavigate();

    const createColumns = () => {
        const colBuild: GridColDef[] = Object.entries(columnDict).map(([columnname, type]) => {
            console.log("опции для выбора", userOptions.current);
            const colName = columnname as keyof typeof columnDict;
            let colDef: GridColDef = {
                field: colName,
                headerName: headers.current[colName],
                flex: 1,
                type: type as GridColType,
            };
            if (type === "singleSelect") {
                colDef = {
                    ...colDef,
                    valueOptions: userOptions.current ? userOptions.current[colName] : [],
                } as GridSingleSelectColDef;
            }
            if (columnname === "ProgramName") {
                colDef = {
                    ...colDef,
                    renderCell: (params) => (
                        <MuiLink
                            component={Link}
                            state={params.row}
                            to={`${endpoints.TECHMAN}/${params.row.ProgramName}`}
                        >
                            {params.row.ProgramName}
                        </MuiLink>
                    ),
                };
            }
            return colDef;
        });

        colBuild.push({
            field: "actions",
            headerName: "Выбрать для загрузки",
            type: "actions",
            width: 150,
            renderCell: (params: GridRenderCellParams<ProcessedPrognameType>) => (
                <Checkbox checked={params.row.checked} onChange={() => handleSelect(params)} />
            ),
        });
        return colBuild;
    };

    // свидетельствует о том, что данные получены с сервера, можно их обработать
    const [loaded, setLoaded] = useState(false);
    // можно показывать таблицу
    const [showTable, setShowTable] = useState(false);
    const [notification, setNotification] = useState(false); // всплывающее уведомление, что данные ушли на сервер

    //если появились данные, нужно сформировать колонки таблицы
    // Добавляем к исходным данным колокии
    const processData: (data: TechProgramType[]) => ProcessedPrognameType[] = (data) => {
        if (loaded) {
            const tableOptions: selecOptionsType = {};
            const enriched = data.map((item) => {
                (Object.keys(columnDict) as ProgNameKeysType[]).forEach((key) => {
                    // формируем опции для ыпадающих списков
                    if (columnDict[key] === "singleSelect") {
                        if (tableOptions[key] === undefined) {
                            tableOptions[key] = [blancOption, item[key]];
                            setFilterValue((prev) => ({ ...prev, [key]: blancOption }));
                        } else {
                            if (!tableOptions[key].includes(item[key])) {
                                tableOptions[key].push(item[key]);
                            }
                        }
                    }
                });
                // возвращаем данные с добавлением колонок id и checked
                return {
                    ...item,
                    id: item.ProgramName,
                    checked: false,
                    PostDateTime: dayjs(item.PostDateTime).format("DD.MM.YYYY"),
                };
            });
            console.log("список опций для селекта", tableOptions);
            userOptions.current = tableOptions;
            return enriched;
        }
        return [];
    };

    /*загружаем даные о програмах с сервера*/
    const loadData = async (diapazon: DateDiapazonType) => {
        setShowTable(false);
        setLoaded(false);
        setNoData(false);
        try {
            const data = await getNewPrograms({
                start_date: diapazon.startDate.format("YYYY-MM-DD"),
                end_date: diapazon.endDate.format("YYYY-MM-DD"),
            });
            if (data) {
                setRawData(data.data);
                headers.current = data.headers;
                console.log("данные с сревера:", data);
                setLoaded(true);
            }
        } catch (error) {
            if (error.response && error.response.status === 401) {
                console.error("Ошибка авторизации: требуется вход в систему.");
                navigate(endpoints.LOGIN);
            }
            console.error("Error fetching protected data:", error);
        }
    };

    // первоначальная загрузка данных
    useEffect(() => {
        loadData(dateDiapazon);
    }, []);

    useEffect(() => {
        if (loaded && rawData.length > 0) {
            const processed = processData(rawData);
            setData(processed);
            setFilteredData(processed);
            columns.current = createColumns();
            setShowTable(true);
        } else if (loaded && rawData.length === 0) {
            setNoData(true);
        }
    }, [loaded, rawData]);

    /**
     * Отправлем данные программы для загрузки из базы Плазмы в нашу базу.
     */
    const handleCreateData = async () => {
        const createRecords: ICreateData[] = data
            .filter((item) => item.checked === true)
            .map((item) => ({ program_status: item.program_status, ProgramName: item.ProgramName }));
        console.log(createRecords);
        await techmanCreateData(createRecords);
        setNotification(true);
        loadData(dateDiapazon);
    };

    //обработка выбора строк с помощью чекбокса
    const handleSelect = (props: GridRenderCellParams<TechProgramType>) => {
        // изменение данных в исходной таблице
        // вообще, данные в ней нужно менять только после изменения значения фильтра (или его сборса)
        setData((prevRows) =>
            prevRows.map((row) => {
                if (row.id === props.id) {
                    return { ...row, checked: !row.checked };
                }
                return row;
            })
        );
        // обновляем отфильтрованные данные в таблице после нажатия на чекбокс
        setFilteredData((prevRows) =>
            prevRows.map((row) => {
                if (row.id === props.id) {
                    return { ...row, checked: !row.checked };
                }
                return row;
            })
        );
    };

    /**Считает количество выделенных чекбоксами строк*/
    useEffect(() => {
        if (data?.length > 0) {
            setSelectedPrograms(data.reduce((sum, item) => sum + Number(item.checked), 0));
        }
    }, [data]);

    const handleFilterChange = (e: SelectChangeEvent, filterField: string) => {
        const value = e.target.value;
        if (value === blancOption) {
            apiRef.current.setFilterModel({
                items: [],
            });
        } else {
            apiRef.current.setFilterModel({
                items: [{ field: filterField, operator: "is", value: value }],
            });
        }
        setFilterValue((prev) => {
            const a = Object.keys(prev).map((key) => [key, blancOption]);
            const b = Object.fromEntries(a);
            b[filterField] = value;
            return b;
        });
    };

    /**
     * Сигнализирует, что количество выделенных строк в таблице изменилось.
     * Работает только если включить опцию выделения рядов через чекбоксы checkboxSelection
     * @param newSelectionModel
     */
    const rowChange = (newSelectionModel: GridRowSelectionModel) => {
        console.log(newSelectionModel);
    };

    const selectCurrentday = ()=> {
        const diap:DateDiapazonType = {startDate:dayjs(), endDate:dayjs()}  
        setDateDiapazon(diap)
        loadData(diap)
    }

    const selectWeek= ()=> {
        const diap:DateDiapazonType = {startDate:dayjs().subtract(7,"days"), endDate:dayjs()}  
        setDateDiapazon(diap)
        loadData(diap)
    }


    return (
        <>
            <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 2, mt: 1 }}>
                <Typography variant="h5">Загрузка программ</Typography>
                <DateDiapazon dates={dateDiapazon} setDates={setDateDiapazon} />
                <Stack spacing={2} direction="row">
                    <Button variant="contained" onClick={selectCurrentday}>
                        за сегодня
                    </Button>
                    <Button variant="contained" onClick={selectWeek}>
                        за неделю
                    </Button>

                    <Button variant="contained" onClick={()=>loadData(dateDiapazon)}>
                        за период
                    </Button>

                    <Button
                        variant="contained"
                        onClick={() => {
                            handleCreateData();
                        }}
                        disabled={!Boolean(selectedPrograms).valueOf()}
                    >
                        Отправить выбранные программы
                    </Button>
                </Stack>
                <Notification value={notification} setValue={setNotification} />
                {noData && <Typography variant="h6">Данные за указанный период отсутствуют.</Typography>}
                {showTable && (
                    <div style={{ height: "600px", width: "100%" }}>
                        <Stack spacing={2} direction="row" sx={{ pb: 2, px: 1 }}>
                            {/* <FormControl variant="outlined" style={{ minWidth: 200 }}>
                                <InputLabel>Пользователь</InputLabel>
                                <Select
                                    value={filterValue["UserName"]}
                                    label="Пользователь"
                                    onChange={(e) => handleFilterChange(e, "UserName")}
                                >
                                    {userOptions.current["UserName"].map((item) => (
                                        <MenuItem key={item} value={item}>
                                            {item}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                            <FormControl variant="outlined" style={{ minWidth: 200 }}>
                                <InputLabel>Статус</InputLabel>
                                <Select
                                    label="Filter2"
                                    value={filterValue["program_status"]}
                                    onChange={(e) => handleFilterChange(e, "program_status")}
                                >
                                    {userOptions.current["program_status"].map((item) => (
                                        <MenuItem key={item} value={item}>
                                            {item}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl> */}
                            <GlobalFilter
                                rows={data}
                                setRows={setData}
                                filteredRows={filteredData}
                                setFilteredRows={setFilteredData}
                            />
                        </Stack>

                        <DataGrid
                            //rows={data}
                            rows={filteredData}
                            columns={columns.current}
                            //density="compact"
                            // checkboxSelection
                            // disableRowSelectionOnClick
                            // onRowSelectionModelChange={rowChange}
                            slots={{ toolbar: CustomToolbar }}
                            apiRef={apiRef}
                        />
                    </div>
                )}
            </Box>
        </>
    );
};

export default Techman;
