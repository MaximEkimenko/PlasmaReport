import React, { useState, useEffect, useRef, useCallback, useMemo } from "react";
import { Link } from "react-router-dom";
import { Link as MuiLink } from "@mui/material";
import { Box, Typography, Button } from "@mui/material";
import { GridColDef, useGridApiRef, GridRenderCellParams } from "@mui/x-data-grid";

import DumbDoerSelect from "../../components/DoerSelect/DumbDoerSelect";
import PrioritySelect from "../../components/PrioritySelect/PropritySelect";
import { assignProgramsRequest, getProgramsAndDoers } from "../../utils/requests";
import { DoerType, ProgramExtendedType, changeFieldType, ProgramType } from "./Master.types";
import { ProgramPriorityType } from "../Logist/Logist.types";
import Notification from "../../components/Notification/Notification";
import FilteredDataGrid from "../../components/FilterableDataGrid/FilterableDataGrid";
import { endpoints } from "../../utils/authorization";
import { useModifiedRows } from "../../hooks";
import { updateTableData, UniversalUpdaterType } from "../../utils/update-any-field-in-table";
import { ImageWidget } from "../../components/IamgeWidget/ImageWidget";
import { BASE_URL } from "../../utils/urls";
import { ProgramLink } from "../../components/ProgramLink/ProgramLink";

//список приоритетов, полученный из множетсва ProgramPriorityType
const priorityArray: ProgramPriorityType[] = Object.values(ProgramPriorityType);
//колонки, которые будут обображаться в таблице
const columnFields: (keyof ProgramExtendedType)[] = [
    "id",
    "program_pic",
    "ProgramName",
    "program_priority",
    "doerIds",
    "doerFio",
    "program_status",
    "wo_numbers",
    "wo_data1",
    "Thickness",
    "SheetWidth",
    "SheetLength",
];

const hiddenIdColumn = {
    columns: {
        columnVisibilityModel: {
            id: false,
            doerFio: false,
        },
    },
};

export function Master() {
    const columns = useRef<GridColDef[]>([]); // стабильная переменная, чтобы хоанить описание столбцов
    const [data, setData] = useState<Partial<ProgramExtendedType>[] | null>(null);
    const apiRef = useGridApiRef();
    // в переменной содержатся сфмилии исполнителей, они не меняются, поэтому useState не нужен
    const doers = useRef<DoerType[]>([]);
    //измененные строки в таблице, чтобы знать, что отправлять на сервер
    const { modifiedRows, clearModifiedRows, updateModifiedRows } = useModifiedRows();
    const [notification, setNotification] = useState(false); // уведомление, что данные ушли на сервер

    const dataUpdater = useMemo(() => updateTableData(columnFields, setData), []);

    /**
     * Загрузка программ и операторов для отображения на странице мастера
     */
    const loader = async () => {
        const response = await getProgramsAndDoers();
        if (response !== undefined) {
            //setData(processData(response.data));
            setData(prepareData(response.data));
            doers.current = [...response.doers.sort((a, b) => a.fio_doer.localeCompare(b.fio_doer))];
            columns.current = createColumns(response.headers);
        }
    };

    useEffect(() => {
        // загрузка данных при загрузке страницы
        loader();
    }, []);

    const prepareData = (data: ProgramType[]) => {
        const processedData = data.map((item) => {
            const row = columnFields.reduce<Partial<ProgramExtendedType>>((acc, field) => {
                acc[field] = item[field];
                return acc;
            }, {});
            row["program_pic"] = `${BASE_URL}${item.program_pic}`;
            row["doerFio"] = item.fio_doers.map((doer) => doer.fio_doer).join(", ");
            row["doerIds"] = item.fio_doers.map((doer) => doer.id);
            return row;
        });
        return processedData;
    };

    /**
     * Формирует словарь с записями, которые будут отправлены на сервер для назначения исполнителя на
     * конкретную программу. Если работник назначается на программу, в массив assignedPrograms добавляется
     * соответствующая запись. Если в селекте выбриается пустая опция - запись удаляетс яиз масива.
     */

    const updateTable = useCallback<UniversalUpdaterType>(
        (rowId: number, processObject) => {
            updateModifiedRows(rowId);
            dataUpdater(rowId, processObject);
        },
        [dataUpdater, updateModifiedRows]
    );

    /**
     * Описываем столбцы таблицы. Внутри отдельных столбцов помещаются другие компоненты.
     * В эти копопоненты в качестве колбэков передаются функции. Так как колбэки создают
     * замыкания, если в этих функциях используется состояние, то оно може стать неактуальным.
     * Если функция не обновится, то она будет обрабатывать ланне на момент создания колбэка,
     * так что надо быть аккуратнее.
     */
    const createColumns = useCallback(
        (headers) => {
            const clmns: GridColDef[] = columnFields.map((columnname) => {
                let colTemplate: GridColDef = {
                    field: columnname,
                    headerName: headers[columnname],
                    flex: 1,
                };

                if (columnname === "program_pic") {
                    colTemplate = {
                        ...colTemplate,
                        width: 320,
                        flex: 0,
                        renderCell: (params) => <ImageWidget source={params.value} />,
                    };
                }

                if (["wo_numbers", "wo_data1"].includes(columnname)) {
                    colTemplate = {
                        ...colTemplate,
                        valueGetter: (value) => value.join(", "),
                    };
                }

                if (columnname === "ProgramName") {
                    colTemplate = {
                        ...colTemplate,
                        renderCell: (params) => <ProgramLink params={params} endpoint={endpoints.MASTER} />
                    };
                }
                if (columnname === "program_priority") {
                    colTemplate = {
                        ...colTemplate,
                        width: 170,
                        flex: 0,
                        renderCell: (params) => (
                            <PrioritySelect
                                selectValue={params.row.program_priority}
                                rowId={params.row.id}
                                priorityOptions={priorityArray}
                                assignHandler={updateTable}
                            />
                        ),
                    };
                }
                if (columnname === "doerIds") {
                    colTemplate = {
                        ...colTemplate,
                        headerName: "Исполнители",
                        width: 330,
                        flex: 0,
                        renderCell: (params) => (
                            <DumbDoerSelect
                                selectValue={params.row.doerIds}
                                rowId={params.row.id}
                                doers={doers.current}
                                assignHandler={updateTable}
                            />
                        ),
                    };
                }
                return colTemplate;
            });

            return clmns;
        },
        [updateTable]
    );

    const handleAssignPrograms = async () => {
        if (data !== null) {
            const programs = data
                // рассматриваем только те записи, у которых есть фамилии. Без фамилий приоритет поменять
                // нельзя, поле с исполнителями обязательно при отправке на сервер
                ?.filter((item) => modifiedRows.has(item.id) && item.doerIds?.length)
                .map((item) => {
                    return { id: item.id, fio_doers_ids: item.doerIds, program_priority: item.program_priority };
                });
            console.log(programs);
            //если фамилии не выбраны, запрос не посылаем

            if (programs.length === 0) {
                return;
            }

            await assignProgramsRequest(programs);
            // сброс заполненных работников и перезагрузка страницы
            //setAssignedPrograms([]);
            clearModifiedRows();
            setNotification(true);
            loader();
        }
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
                <Typography variant="h5">Рабочее место мастера</Typography>
                <Button variant="contained" onClick={handleAssignPrograms} disabled={!modifiedRows.size}>
                    Отправить в работу
                </Button>
                <Notification value={notification} setValue={setNotification} />
                {data == null && "данных нет"}
                {data !== null && (
                    <div style={{ height: 700, width: "100%" }}>
                        <FilteredDataGrid {...gridParams} />
                    </div>
                )}
            </Box>
        </>
    );
}
