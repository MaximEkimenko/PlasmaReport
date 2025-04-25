import { useState, useEffect, useRef, useCallback, useContext, useMemo } from "react";
import { Box, Typography, Button, Stack, Checkbox } from "@mui/material";
import { DataGrid, GridColDef, useGridApiRef, GridColumnVisibilityModel } from "@mui/x-data-grid";
import { Link } from "react-router-dom";

import { getReportData } from "../../utils/requests";
import { ProgramType } from "../Master/Master.types";
import { hiddenIdColumn } from "../../utils/tableInitialState";
import { MasterProgramPartsRecordType } from "../LogistTable/LogistTable.types";

import ReportToolbar from "../../components/CustomToolbar/ReportToolbar";
import { DateDiapazon } from "../../components/DateDiapazon/DateDiapazon";
import axios from "axios";
import { getVisibilityModelToStore, saveVisibilityModelToStore } from "../../utils/local-storage";
import { endpoints, getUserRole } from "../../utils/authorization";
import { ReportDateDiapazonContext } from "../../context";
import { useAuth } from "../../hooks";

export type ProgramAndFioType = ProgramType & { dimensions: string };

const VISIBILITY_MODEL_STORAGE_KEY = "main_report_visibility";

export function MainReport() {
    const dateDiapazonContext = useContext(ReportDateDiapazonContext);
    if (!dateDiapazonContext) {
        throw new Error("не определено начальное значение для диапазона загрузки программ");
    }
    const { dateDiapazon, setDateDiapazon } = dateDiapazonContext;

    const [data, setData] = useState<MasterProgramPartsRecordType[]>([]);
    const [loadError, setLoadError] = useState(false);
    const [showTable, setShowTable] = useState(false);
    const [columnVisibilityModel, setColumnVisibilityModel] = useState(
        getVisibilityModelToStore(VISIBILITY_MODEL_STORAGE_KEY)
    );
    const columns = useRef<GridColDef[]>([]);
    const errorMessage = useRef("Ошибка загрузки");
    const { currentUser } = useAuth();
    console.log(currentUser);
    console.log(getUserRole(currentUser), currentUser);

    const createColumns = useCallback((headers: Record<string, string>) => {
        const columns: GridColDef[] = Object.keys(headers).map((columnname) => {
            let colTemplate: GridColDef = {
                field: columnname,
                headerName: headers[columnname],
                width: 160,
            };
            if (columnname == "fio_doers") {
                colTemplate = {
                    ...colTemplate,
                    valueGetter: (value) => {
                        if (Array.isArray(value)) {
                            return value.map((item) => item.fio_doer).join(", ");
                        }
                        return value.fio_doer;
                    },
                };
            }
            if (columnname == "done_by_fio_doer") {
                colTemplate = {
                    ...colTemplate,
                    valueGetter: (value) => value?.fio_doer,
                };
            }

            return colTemplate;
        });
        return columns;
    }, []);

    const loader = async () => {
        setShowTable(false);
        const datesObj = {
            start_date: dateDiapazon.startDate.format("YYYY-MM-DD"),
            end_date: dateDiapazon.endDate.format("YYYY-MM-DD"),
        };
        try {
            const response = await getReportData(datesObj);
            if (response !== undefined) {
                setData(response.data);
                columns.current = createColumns(response.headers);
                setShowTable(true);
                setLoadError(false);
            } else {
                setLoadError(true);
            }
        } catch (error) {
            errorMessage.current = "Ошибка загрузки";
            if (axios.isAxiosError(error)) {
                if (error.response?.status === 404) {
                    errorMessage.current = "Отсутствуют записи за выбранный период";
                }
            }
            setLoadError(true);
        }
    };

    useEffect(() => {
        loader();
    }, []);

    useEffect(() => console.log(columnVisibilityModel), [columnVisibilityModel]);
    const handleVisibilityModel = (newModel: GridColumnVisibilityModel) => {
        setColumnVisibilityModel(newModel);
        saveVisibilityModelToStore(newModel, VISIBILITY_MODEL_STORAGE_KEY);
    };

    const getFilname = () => {
        return `программы за ${dateDiapazon.startDate.format("DD.MM.YYYY")}-${dateDiapazon.endDate.format(
            "DD.MM.YYYY"
        )}.xlsx`;
    };

    // кнопка перехода к тетальному отчету, которая появляется только тогда, когда пользователь - админ или технолог
    const detailReportButton = useMemo( () => {
        if (["ADMIN", "TECHMAN"].includes(getUserRole(currentUser))) {
            return (
                <Link to={endpoints.DETAIL_REPORT}>
                    <Button variant="contained">Отчет по заказам</Button>
                </Link>
            );
        }
    }, [currentUser]);

    return (
        <>
            <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 2, mt: 1 }}>
                <Typography variant="h5">Отчет</Typography>
                <Stack direction={"row"} gap={2}>
                    <DateDiapazon dates={dateDiapazon} setDates={setDateDiapazon} />
                    <Button variant="contained" onClick={loader}>
                        Получить данные за период
                    </Button>
                </Stack>
                {detailReportButton}
                {loadError && <div>{errorMessage.current}</div>}

                {showTable && (
                    <div style={{  width: "100%" }}>
                        <DataGrid
                            rows={data}
                            columns={columns.current}
                            slots={{ toolbar: ReportToolbar }}
                            slotProps={{ toolbar: { columns: columns.current, filename: getFilname() } }}
                            initialState={hiddenIdColumn}
                            getRowHeight={() => "auto"}
                            //disableVirtualization
                            columnVisibilityModel={columnVisibilityModel}
                            onColumnVisibilityModelChange={handleVisibilityModel}
                        />
                    </div>
                )}
            </Box>
        </>
    );
}
