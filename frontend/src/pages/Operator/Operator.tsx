import { useRef, useState, useEffect, useContext, useMemo, useCallback } from "react";
import { Box, Button, Chip, FormControl, InputLabel, MenuItem, OutlinedInput, Select, Typography } from "@mui/material";
import { Link } from "react-router-dom";
import { Link as MuiLink } from "@mui/material";
import { GridColDef, useGridApiRef } from "@mui/x-data-grid";
import { getDoers, getMyPrograms, OperatorStartProgram } from "../../utils/requests.ts";
import { DoerType, ProgramType } from "../Master/Master.types.ts";
import { OperatorSelectContext } from "../../context.tsx";
import { hiddenIdColumn } from "../../utils/tableInitialState.ts";
import FilteredDataGrid from "../../components/FilterableDataGrid/FilterableDataGrid.tsx";
import { endpoints } from "../../utils/authorization.ts";
import { useAuth } from "../../hooks";
import { BASE_URL } from "../../utils/urls.ts";
import { ImageWidget } from "../../components/IamgeWidget/ImageWidget.tsx";
import styles  from "./Oerator.module.css";
import {priorityStylesMap} from "../../utils/priority-color"
import { ProgramLink } from "../../components/ProgramLink/ProgramLink.tsx";

const columnFields = [
    "id",
    "program_pic",
    "program_priority",
    "ProgramName",
    "program_status",
    // "wo_numbers",
    // "wo_data1",
    "fio_doer",
    "Thickness",
    "SheetWidth",
    "SheetLength",
];



export function Operator() {
    const operatorIdContext = useContext(OperatorSelectContext);
    if (!operatorIdContext) {
        throw new Error("не определено начальное значение для конекста оператора");
    }
    const authContext = useAuth();
    if (!authContext) {
        throw new Error("Не определено значение для конекста авторизации");
    }
    const { currentUser } = authContext;

    const { selectedOperatorId, setSelectedOperatorId } = operatorIdContext;
    const columns = useRef<GridColDef[]>([]);
    const [data, setData] = useState<ProgramType[] | null>(null);
    const [doers, setDoers] = useState<DoerType[]>([]);
    const apiRef = useGridApiRef();
    const [operatorsLoaded, setOperatorsLoaded] = useState(false);
    const [showTable, setShowTable] = useState(false);

    const loadOperators = async () => {
        const response = await getDoers();
        if (response) {
            setDoers(response.sort((a, b) => a.fio_doer.localeCompare(b.fio_doer)));
            //определяем опцию по умолчанию в выпадающем списке операторов
            const currentOperator = response.find((item) => item.user_id === currentUser.id);
            // если текущий оператор уже хранится в контексте, то при заходе на страницу, оставляем его как есть
            if (!selectedOperatorId) {
                // если юзер не является оперптором, то просто выбираем первого опреатора из списка
                setSelectedOperatorId(currentOperator ? currentOperator.id : response[0].id);
            }
            setOperatorsLoaded(true);
        }
    };

    useEffect(() => {
        loadOperators();
    }, []);

    const reloadTable = useCallback(async (fio_id: number) => {
        const response = await getMyPrograms(fio_id);
        if (response !== undefined) {
            setData(response.data.sort((a, b) => a.id - b.id));
        }
    }, []);

    const changeProgramStatus = useCallback(
        async (rowId: number, new_status?: string) => {
            const result = await OperatorStartProgram(rowId, new_status);
            if (result?.msg) {
                console.log(result);
                if (selectedOperatorId) {
                    reloadTable(selectedOperatorId);
                    setShowTable(true);
                }
            }
        },
        [reloadTable, selectedOperatorId]
    );

    const createColumns = useCallback(
        (headers: Record<string, string>) => {
            const clmns: GridColDef[] = columnFields.map((columnname) => {
                let col: GridColDef = {
                    field: columnname,
                    headerName: headers[columnname],
                    flex: 1,
                };
                if (columnname === "program_pic") {
                    col = {
                        ...col,
                        width: 320,
                        flex: 0,
                        renderCell: (params) => <ImageWidget source={params.value} />,
                    };
                }
                if (columnname === "program_priority") {
                    col = {
                        ...col,
                        width: 130,
                        flex: 0,
                        renderCell: (params) => <div className={`${priorityStylesMap[params.value]} ${styles.prioritybox}`}>{params.value}</div>,
                        
                    };
                }

                if (columnname == "ProgramName") {
                    col = {
                        ...col,
                    renderCell: (params) => <ProgramLink params={params} endpoint={endpoints.OPERATOR} />
                    };
                }
                if (["wo_numbers", "wo_data1"].includes(columnname)) {
                    const colTemplate = {
                        ...colTemplate,
                        valueGetter: (value) => value.join(", "),
                    };
                }
                if (columnname == "fio_doer") {
                    col = {
                        ...col,
                        valueGetter: (value) => value.fio_doer,
                    };
                }

                return col;
            });
            clmns.push({
                field: "action",
                headerName: "Действия",
                flex: 0,
                width: 180,
                renderCell: (params) => {
                    switch (params.row.program_status) {
                        case "распределена":
                            return (
                                <Button
                                    sx={{ my: 0.5 }}
                                    variant="contained"
                                    onClick={() => changeProgramStatus(params.id)}
                                >
                                    в работу
                                </Button>
                            );
                        case "в работе":
                            return (
                                <Button
                                    sx={{ my: 0.5 }}
                                    variant="contained"
                                    onClick={() => changeProgramStatus(params.id, "распределена")}
                                >
                                    остановить
                                </Button>
                            );
                        default:
                            return <p></p>;
                    }
                },
            });
            return clmns;
        },
        [changeProgramStatus]
    );

    /**
     * Очистка данных от лишних колонок чтобы можно было наримальн делать глобальную фильтрацию
     * */
    const prepareData = (data) => {
        const prepared = data.map((row) => {
            let preparedRow = columnFields.reduce<Partial<ProgramType>>((acc, field) => {
                acc[field] = row[field];
                return acc;
            }, {});
            preparedRow["program_pic"] = `${BASE_URL}${row.program_pic}`;
            return preparedRow;
        });
        return prepared;
    };

    /**
     * Загрузка программы для отображения в таблице по идентификатору оператора
     * @param fio_id - идентификатор оператора
     */
    const loadTable = useCallback(
        async (fio_id: number) => {
            setShowTable(false);
            const response = await getMyPrograms(fio_id);
            if (response !== undefined) {
                setData(prepareData(response.data).sort((a: ProgramType, b: ProgramType) => a.id - b.id));
                columns.current = createColumns(response.headers);
                setShowTable(true);
            }
        },
        [createColumns]
    );

    useEffect(() => {
        if (operatorsLoaded) {
            loadTable(selectedOperatorId);
        }
    }, [selectedOperatorId, operatorsLoaded, loadTable]);

    const hadleSelectDoer = (event) => {
        console.log("выбрали работника:", event.target.value);
        const selectedDoer = doers.filter((item) => item.id == event.target.value)[0];
        // даем изменить значение селекта тольо если юзер не является оператором
        if (!doers.find((item) => item.user_id === currentUser.id)) setSelectedOperatorId(selectedDoer.id);
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
                <Typography variant="h5">Рабочее место оператора</Typography>
                {operatorsLoaded && (
                    <>
                        <FormControl sx={{ m: 1, width: 300 }} size="small">
                            <InputLabel id="master-program-doers">Оператор</InputLabel>
                            <Select
                                labelId="master-program-doers"
                                input={<OutlinedInput label="Оператор" />}
                                onChange={hadleSelectDoer}
                                value={selectedOperatorId}
                                displayEmpty={true}
                            >
                                {doers.map((doer) => (
                                    <MenuItem value={doer.id} key={doer.id}>
                                        {doer.fio_doer}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </>
                )}
                {showTable && (
                    <div style={{ height: 700, width: "100%" }}>
                        <FilteredDataGrid {...gridParams} />
                    </div>
                )}
            </Box>
        </>
    );
}
