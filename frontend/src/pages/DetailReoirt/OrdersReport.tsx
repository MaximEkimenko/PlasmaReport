import { useState, useEffect, useRef, useCallback, useContext, useMemo } from "react";
import { Box, Typography, Button, Stack, Checkbox, Link as MuiLink } from "@mui/material";
import { DataGrid, GridColDef, useGridApiRef, GridColumnVisibilityModel, GridToolbar } from "@mui/x-data-grid";
import { Link } from "react-router-dom";

import { getOrders, getReportData } from "../../utils/requests";
import { OrderReportType, ProgramType } from "../Master/Master.types";
import { hiddenIdColumn } from "../../utils/tableInitialState";
import { MasterProgramPartsRecordType } from "../LogistTable/LogistTable.types";


import { DateDiapazon } from "../../components/DateDiapazon/DateDiapazon";
import { DateDiapazonType } from "../Techman/Techman.types";
import dayjs from "dayjs";
import axios from "axios";

import FilteredDataGrid from "../../components/FilterableDataGrid/FilterableDataGrid";
import { ReportDateDiapazonContext } from "../../context";

export type ProgramAndFioType = ProgramType & { dimensions: string };



const columnFields: (keyof OrderReportType )[] = [
            "WONumber",
            "CustomerName",
            "WODate",
            "OrderDate",
            "WOData1",
            "WOData2",
            "DateCreated",]


export function OrdersReport () {
    const dateDiapazonContext = useContext(ReportDateDiapazonContext);
    if (!dateDiapazonContext) {
        throw new Error("не определено начальное значение для диапазона загрузки программ");
    }
    const { dateDiapazon, setDateDiapazon } = dateDiapazonContext;   


    const [data, setData] = useState<MasterProgramPartsRecordType[]>([]);
    const [loadError, setLoadError] = useState(false);
    const [showTable, setShowTable] = useState(false);
    const columns = useRef<GridColDef>([]);
    const apiRef = useGridApiRef();
    const errorMessage = useRef("Ошибка загрузки");


    const createColumns = useCallback((headers) => {
        const columns: GridColDef[] = columnFields.map((columnname) => {
            let colTemplate: GridColDef = {
                field: columnname,
                headerName: headers[columnname],
                minWidth: 200,
            };
            if (columnname === "WONumber") {
                colTemplate = {
                    ...colTemplate,
                    renderCell: (params) => (
                        <MuiLink
                            component={Link}
                            state={params.row}
                            to={`${params.row.WONumber}`}
                        >
                            {params.row.WONumber}
                        </MuiLink>
                    ),
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
            const response = await getOrders(datesObj);
            if (response !== undefined) {
                setData(response.data);
                columns.current = createColumns(response.headers);
                setShowTable(true);
                setLoadError(false);
            } else {
                setLoadError(true);
            }
        } catch (error) {
            console.log(error)
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



    const gridParams = useMemo(
        () => ({
            rows: data,
            setRows: setData,
            columns: columns.current,
            initialState: hiddenIdColumn,
            apiRef: apiRef,
            getRowId: row=> row.WONumber,

        }),
        [apiRef, data]
    );


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
                <Link to="/report">
                    <Button variant="contained">К основному отчету</Button>
                </Link>
                {loadError && <div>{errorMessage.current}</div>}

                {showTable && (
                    <div style={{ height: 700, width: "100%" }}>
                        <FilteredDataGrid {...gridParams} />
                    </div>
                )}
            </Box>
        </>
    );
};

