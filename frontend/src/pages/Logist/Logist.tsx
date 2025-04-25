import { useState, useEffect, useRef, useMemo, useCallback } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Grid2, Link as MuiLink } from "@mui/material";
import { Box, Typography, Button, Stack, Checkbox } from "@mui/material";
import { GridColDef, useGridApiRef } from "@mui/x-data-grid";

import { logistGetPrograms } from "../../utils/requests";
import { ProgramType } from "../Master/Master.types";
import { hiddenIdColumn } from "../../utils/tableInitialState";

import FilteredDataGrid from "../../components/FilterableDataGrid/FilterableDataGrid";
import { endpoints } from "../../utils/authorization";
import { MasterProgramPartsRecordType } from "../LogistTable/LogistTable.types";
import { ImageWidget } from "../../components/IamgeWidget/ImageWidget";
import { BASE_URL } from "../../utils/urls";
import styles from "../Operator/Oerator.module.css";
import { priorityStylesMap } from "../../utils/priority-color";
import { ProgramLink } from "../../components/ProgramLink/ProgramLink";
import { LogistProgramType } from "./Logist.types";
import { UniversalUpdaterType, updateTableData } from "../../utils/update-any-field-in-table";
import { useModifiedRows } from "../../hooks";

type ProgramPartsProcessedType = LogistProgramType & { checkBox: boolean };
const columnFields: (keyof ProgramPartsProcessedType)[] = [
    "id",
    "checkBox",
    "program_pic",
    "ProgramName",
    "program_priority",
    "program_status",
    "wo_numbers",
    "wo_data1",
    "Thickness",
    "SheetWidth",
    "SheetLength",
    //"fio_doers",
];

function Logist() {
    const columns = useRef<GridColDef[]>([]);
    const [data, setData] = useState<ProgramType[]>([]);
    const apiRef = useGridApiRef();
    const [loadError, setLoadError] = useState(false);
    const [showTable, setShowTable] = useState(false);

    const location  = useLocation()
    const navigate = useNavigate()

    const modRows = useModifiedRows();
    const dataUpdater = useMemo(() => updateTableData(columnFields, setData), []);

    const updateTable = useCallback(
        (rowId: number | string, value: boolean, processObject) => {
            if (!value) {
                modRows.updateModifiedRows(rowId);
            } else {
                modRows.removeManyModifiedRows([rowId]);
            }

            dataUpdater(rowId, processObject);
        },
        [dataUpdater, modRows.updateModifiedRows]
    );

    const createColumns = useCallback((headers: Record<string, string>) => {
        const clmns: GridColDef[] = columnFields.map((columnname) => {
            let col: GridColDef = {
                field: columnname,
                headerName: headers[columnname],
                flex: 1,
            };

            if (columnname === "checkBox") {
                col = {
                    ...col,
                    type: "actions",
                    width: 150,
                    renderCell: (params) => (
                        <Checkbox
                            checked={params.row.checkBox}
                            onChange={() => {
                                updateTable(params.id, params.row.checkBox, { checkBox: () => !params.row.checkBox });
                            }}
                        />
                    ),
                };
            }

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
                    renderCell: (params) => (
                        <div className={`${priorityStylesMap[params.value]} ${styles.prioritybox}`}>{params.value}</div>
                    ),
                };
            }

            if (columnname === "ProgramName") {
                col = {
                    ...col,
                    renderCell: (params) => <ProgramLink params={params} endpoint={endpoints.LOGIST} />,
                };
            }
            return col;
        });
        return clmns;
    }, []);

    const prepareData = (data) => {
        const prepared = data.map((row) => {
            let preparedRow = columnFields.reduce<Partial<ProgramPartsProcessedType>>((acc, field) => {
                acc[field] = row[field];
                return acc;
            }, {});
            preparedRow["checkBox"] = false;
            preparedRow["program_pic"] = `${BASE_URL}${row.program_pic}`;
            preparedRow["wo_numbers"] = row["wo_numbers"].join(", ");
            preparedRow["wo_data1"] = row["wo_data1"].join(", ");
            return preparedRow;
        });
        return prepared;
    };

    const loader = useCallback(async () => {
        setShowTable(false);
        const response = await logistGetPrograms();

        if (response !== undefined) {
            setData(prepareData(response.data));
            columns.current = createColumns(response.headers);
            setLoadError(false);
            setShowTable(true);
        } else {
            setLoadError(true);
        }
    }, [createColumns]);

    useEffect(() => {
        loader();
    }, [loader]);


    const handleSomeProghamsDetails =() =>{
        if (modRows.modifiedRows.size) {
            console.log("отправляем несколько программ")
            const params = new URLSearchParams();
            modRows.modifiedRows.forEach(programId => params.append('programId', programId));
            const queryString = params.toString();
            console.log("параметры", params)
            console.log("в виде строки", queryString)
            const programName =  data.find(row => modRows.modifiedRows.has(row.id))?.ProgramName
            const url = `${location.pathname}/print?${queryString}`
            navigate(url)
        }
    }

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
                <Grid2 container sx={{ width: "100%" }}>
                    <Grid2 size={3}>
                    <Box display="flex" justifyContent="start" alignItems="center" height="100%" paddingX={1}>
                        
                        <Button variant="contained" size="medium" disabled={!modRows.modifiedRows.size} onClick={handleSomeProghamsDetails}>сформировать ведомость</Button>
                        
                    </Box>
                    </Grid2>
                    <Grid2 size={7}>
                        <Box display="flex" justifyContent="center" alignItems="center" height="100%" paddingX={2}>
                            <Typography variant="h5">Рабочее место логиста</Typography>
                        </Box>
                    </Grid2>
                    <Grid2 size={2}></Grid2>
                </Grid2>
                {/*тестовая кнопка для проверки, когда перерисовывается таблица (она не должна перерисовываться при нажатии на кнопку) */}
                {/* <Button onClick={()=>setCounter((prev) => prev + 1)}>нажми {counter}</Button> */}
                {loadError && <div>Ошибка загрузки</div>}

                {showTable && (
                    <div style={{ height: "800px", width: "100%" }}>
                        <FilteredDataGrid {...gridParams} />
                    </div>
                )}
            </Box>
        </>
    );
}

export default Logist;
