import React, { useState, useEffect, useRef, useContext, useMemo } from "react";
import { Link } from "react-router-dom";
import { TechProgramType, ProcessedPrognameType, DateDiapazonType, ICreateData } from "./Techman.types.ts";
import { DateDiapazon } from "../../components/DateDiapazon/DateDiapazon.tsx";
import Notification from "../../components/Notification/Notification.tsx";
import { techmanCreateData, getNewPrograms, techmanUpdateData } from "../../utils/requests.ts";
import { Box, Typography, Button, Stack, Checkbox, Link as MuiLink, Grid2 } from "@mui/material";
import FilteredDataGrid from "../../components/FilterableDataGrid/FilterableDataGrid.tsx";
import { GridColDef, GridRenderCellParams, useGridApiRef } from "@mui/x-data-grid";
import dayjs from "dayjs";
import { DateDiapazonContext } from "../../context.tsx";
import { endpoints } from "../../utils/authorization.ts";
import { BASE_URL } from "../../utils/urls.ts";
import { ImageWidget } from "../../components/IamgeWidget/ImageWidget.tsx";

type PrognameAndIdType = Exclude<TechProgramType, undefined> & { id: string; checked: boolean };

type ProgNameKeysType = keyof PrognameAndIdType;

// колонки, которые будут отображаться в таблице
const columnDict: Partial<{ [key in ProgNameKeysType]: string }> = {
    PostDateTime: "string",
    ProgramName: "string",
    program_status: "singleSelect",
    UserName: "singleSelect",
    Material: "string",
};

type ProgramFilterStatusType = "новые" | "загруженные";

type originalDataType = Record<ProgramFilterStatusType, ProcessedPrognameType[]>;

type selectAllType = Record<ProgramFilterStatusType, boolean>;
const initialSelectAll: selectAllType = { новые: false, загруженные: false };

// беда в том, что у этих данных id - поле необязательное. У новых программ его нет, а у добавленных оно есть.
// и при отправке на сервер из плазмы новых данных в запросе должен фигуроировать id
// так что я его
const columnFields = [
    "id",
    "program_id",
    "program_pic",
    "PostDateTime",
    "ProgramName",
    "WONumber",
    "program_status",
    "UserName",
    "Material",
    "checked",
];

const hiddenIdColumn = {
    columns: {
        columnVisibilityModel: {
            id: false,
            program_id: false,
        },
    },
};

/**
 * Сам компонент
 * @returns
 */
export function Techman() {
    // интерфейс для управления таблицей
    const apiRef = useGridApiRef();
    // диапазон дат, за который будут загружаться данные
    const dateDiapazonContext = useContext(DateDiapazonContext);
    if (!dateDiapazonContext) {
        throw new Error("не определено начальное значение для диапазона загрузки программ");
    }
    const { dateDiapazon, setDateDiapazon } = dateDiapazonContext;
    const [originalData, setOriginalData] = useState<originalDataType | undefined>(undefined);
    // данные, обработанные для отображения в таблице(все данные целиком, в том числе и те, которые не показываются)
    const [data, setData] = useState<ProcessedPrognameType[]>([]);
    // количество программ, выделенных для загрузки в нашу таблицу из сигмы
    // служит для активации кнопки  отправки данных на сервер
    const [selectedPrograms, setSelectedPrograms] = useState<number>(0);
    // стабильная переменная для храенеия данных о столбцах таблицы]
    const columns = useRef<GridColDef[]>([]);
    const [noData, setNoData] = useState(false);
    // объект, показывающий, что сделать с каждой половинкой данных: либо снять выделение, либо выделить всё
    const [allCheckboxesAction, setAllCheckboxesAction] = useState<selectAllType>(initialSelectAll);
    // подписи для кнопки управления галочками.
    // В зависимости от значения selectAllCheckboxes выводит на кнопке соответствующие надписи
    const allCheckboxesButtonText: Record<number, string> = { 0: "выделить все", 1: "снять выделение" };
    // значение, которое определяет, какие программы сечас отображаются, новые или загруженные
    const programFilterStatus = useRef<ProgramFilterStatusType>("новые");

    const notificationMessage = useRef("Записи обновлены");

    const createColumns = (headers) => {
        const clmns: GridColDef[] = columnFields.map((columnname) => {
            const colName = columnname as keyof typeof columnDict;
            let col: GridColDef = {
                field: colName,
                headerName: headers[colName],
                flex: 1,
            };
            if (columnname === "program_pic") {
                col = {
                    ...col,
                    width: 300,
                    flex: 0,
                    renderCell: (params) => <ImageWidget source={params.value} />,
                };
            }
            if (columnname === "ProgramName") {
                col = {
                    ...col,
                    renderCell: (params) => (
                        <MuiLink
                            component={Link}
                            to={`${endpoints.TECHMAN}/${params.row.ProgramName}`}
                        >
                            {params.row.ProgramName}
                        </MuiLink>
                    ),
                };
            }
            if (columnname === "checked") {
                col = {
                    ...col,
                    width: 150,
                    renderCell: (params: GridRenderCellParams<ProcessedPrognameType>) => (
                        <Checkbox checked={params.row.checked} onChange={() => handleSelect(params)} />
                    ),
                };
            }
            return col;
        });
        return clmns;
    };

    // свидетельствует о том, что данные получены с сервера, можно их обработать
    // можно показывать таблицу
    const [showTable, setShowTable] = useState(false);
    const [notification, setNotification] = useState(false); // всплывающее уведомление, что данные ушли на сервер

    //если появились данные, нужно сформировать колонки таблицы
    // Добавляем к исходным данным колокии
    const prepareData: (data: TechProgramType[]) => originalDataType = (data) => {
        const newProgams: ProcessedPrognameType[] = [];
        const loadedProgams: ProcessedPrognameType[] = [];
        data.forEach((item) => {
            const prepared = {
                ...item,
                id: item.ProgramName,
                program_pic: `${BASE_URL}${item.program_pic}`,
                checked: false,
                PostDateTime: dayjs(item.PostDateTime).format("YYYY-MM-DD"),
                program_id: item.id,
            };

            if (item.program_status === "новая") {
                newProgams.push(prepared);
            } else {
                loadedProgams.push(prepared);
            }
        });
        return { новые: newProgams, загруженные: loadedProgams } satisfies originalDataType;
    };

    /*загружаем даные о програмах с сервера*/
    const loader = async (diapazon: DateDiapazonType) => {
        setShowTable(false);
        setNoData(false);

        const response = await getNewPrograms({
            start_date: diapazon.startDate.format("YYYY-MM-DD"),
            end_date: diapazon.endDate.format("YYYY-MM-DD"),
        });
        if (response) {
            if (response.data.length > 0) {
                const processed = prepareData(response.data);
                setOriginalData(processed);
                setData(processed[programFilterStatus.current]);
                columns.current = createColumns({ ...response.headers, checked: "выбрать для загрузки" });
                setShowTable(true);
            } else {
                setNoData(true);
            }
        }
    };

    // первоначальная загрузка данных
    useEffect(() => {
        loader(dateDiapazon);
    }, []);

    /**
     * Отправлем данные программы для загрузки из базы Плазмы в нашу базу.
     */
    const handleCreateData = async () => {
        const records: ICreateData[] = data
            .filter((item) => item.checked === true)
            .map((item) => ({ program_status: item.program_status, ProgramName: item.ProgramName }));
        console.log(records);
        try {
            await techmanCreateData(records);
            notificationMessage.current = "Программы загружены";
        } catch {
            notificationMessage.current = "ОШИБКА!";
        }
    };

    const handleUpdateData = async () => {
        const records: ICreateData[] = data
            .filter((item) => item.checked === true)
            .map((item) => ({
                program_status: item.program_status,
                ProgramName: item.ProgramName,
                id: item.program_id,
            }));
        console.log(records);
        try {
            await techmanUpdateData(records);
            notificationMessage.current = "Программы обновлены";
        } catch {
            notificationMessage.current = "ОШИБКА!";
        }
    };

    const sendData = async () => {
        if (programFilterStatus.current === "новые") {
            await handleCreateData();
        } else {
            await handleUpdateData();
            setNotification(true);
        }

        setNotification(true);
        loader(dateDiapazon);
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
    };

    const switchTableData = () => {
        const cuttentFilter = programFilterStatus.current !== "новые" ? "новые" : "загруженные";
        const temp = [...data];
        setOriginalData((prev) => ({ ...prev, [programFilterStatus.current]: temp } as originalDataType));
        programFilterStatus.current = cuttentFilter;
    };

    /**
     * при изменении оригинальных данных (например, потвторный запрос после отправки) загружает в таблицу
     * выбранный кусок данных (новые или загруженные программы)
     */
    useEffect(() => {
        if (originalData) {
            setData(originalData[programFilterStatus.current]);
        }
    }, [originalData]);

    /**
     * Ставит (или снимает) галочки на все программы в списке(в переменную data)
     */
    const handleSelectAll = () => {
        setData((prevRows) =>
            prevRows.map((row) => ({ ...row, checked: !allCheckboxesAction[programFilterStatus.current] }))
        );
        setAllCheckboxesAction((prev) => ({
            ...prev,
            [programFilterStatus.current]: !prev[programFilterStatus.current],
        }));
    };

    /**Считает количество выделенных чекбоксами строк*/
    useEffect(() => {
        if (data?.length > 0) {
            setSelectedPrograms(data.reduce((sum, item) => sum + Number(item.checked), 0));
        }
    }, [data]);

    const selectCurrentday = () => {
        const diap: DateDiapazonType = { startDate: dayjs(), endDate: dayjs() };
        setDateDiapazon(diap);
        loader(diap);
    };

    const selectWeek = () => {
        const diap: DateDiapazonType = { startDate: dayjs().subtract(7, "days"), endDate: dayjs() };
        setDateDiapazon(diap);
        loader(diap);
    };

    const gridParams = useMemo(
        () => ({
            rows: data,
            setRows: setData,
            columns: columns.current,
            initialState: hiddenIdColumn,
            apiRef: apiRef,
        }),
        [apiRef, data]
    );

    return (
        <>
            <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 2, mt: 1 }}>
                <Typography variant="h5">Загрузка программ</Typography>
                <Stack spacing={2} direction="row">
                    <DateDiapazon dates={dateDiapazon} setDates={setDateDiapazon} />
                    <Button variant="contained" onClick={() => loader(dateDiapazon)}>
                        за период
                    </Button>
                    <Box width={50} />
                    <Button variant="contained" onClick={selectCurrentday}>
                        за сегодня
                    </Button>
                    <Button variant="contained" onClick={selectWeek}>
                        за неделю
                    </Button>
                </Stack>
                <Grid2 container spacing={3} sx={{ width: "90%" }}>
                    <Grid2 size={10} spacing={2} container>
                        <Grid2 size={3}>
                            <Button variant="contained" onClick={switchTableData} sx={{ width: 150 }}>
                                {programFilterStatus.current}
                            </Button>
                        </Grid2>
                        <Grid2 size={9}>
                            <Button
                                variant="contained"
                                onClick={sendData}
                                disabled={!Boolean(selectedPrograms).valueOf()}
                            >
                                Отправить выбранные программы
                            </Button>
                        </Grid2>
                    </Grid2>
                    <Grid2 size={2}>
                        <Button variant="contained" sx={{ marginRight: "auto", width: 180 }} onClick={handleSelectAll}>
                            {allCheckboxesButtonText[Number(allCheckboxesAction[programFilterStatus.current])]}
                        </Button>
                    </Grid2>
                </Grid2>
                <Notification message={notificationMessage.current} value={notification} setValue={setNotification} />
                {noData && <Typography variant="h6">Данные за указанный период отсутствуют.</Typography>}
                {showTable && (
                    <div style={{ height: 700, width: "100%" }}>
                        <FilteredDataGrid {...gridParams} />
                    </div>
                )}
            </Box>
        </>
    );
}
