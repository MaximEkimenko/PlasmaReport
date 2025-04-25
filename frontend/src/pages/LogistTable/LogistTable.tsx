import { useEffect, useState, useCallback, useRef, useMemo } from "react";
import { Box, Typography, Button, Grid2 } from "@mui/material";
import { GridColDef, useGridApiRef } from "@mui/x-data-grid";
import { logistCalculateParts, masterGetDetailsByProgramId } from "../../utils/requests";
import { MasterProgramPartsRecordType } from "./LogistTable.types";
import { QtyInput } from "../../components/QtyInput/QtyInput";
import Notification from "../../components/Notification/Notification";
import { hiddenIdColumn } from "../../utils/tableInitialState";
import FilteredDataGrid from "../../components/FilterableDataGrid/FilterableDataGrid";
import { useModifiedRows, useProgramInfo } from "../../hooks";
import { updateTableData } from "../../utils/update-any-field-in-table";
import { ImageWidget } from "../../components/IamgeWidget/ImageWidget";
import { BASE_URL } from "../../utils/urls";

const columnFields = [
    "id",
    "ProgramName",
    "PartName",
    "WONumber",
    "part_pic",
    "PartLength",
    "PartWidth",
    "WOData1",
    "Thickness",
    "fio_doers", // надо замениь на done_by_fio
    "QtyInProcess",
    "storage_cell_id",
    "qty_fact",
] as const;

// так как мы удаляем из таблицы лишние строки и преобразуем массив работников в строку с перечислением этих работников,
// то нужно из первоначального типа убрать первонеяальне определение поля "fio_doers" и заменить его на строку
type FilteredMasterProgramParts = Omit<
    Pick<MasterProgramPartsRecordType, (typeof columnFields)[number]>,
    "fio_doers"
> & { fio_doers: string };

export function LogistTable() {
    const programInfo =  useProgramInfo()
    console.log("=============")
    console.log(programInfo)
    
    //просто счетчик для проверки, как перерисовываается таблица при изменении части страницы, которая на таблицу никак не влияет
    const columns = useRef<GridColDef[]>([]);
    const [data, setData] = useState<FilteredMasterProgramParts[]>([]);
    const apiRef = useGridApiRef();

    const [loadError, setLoadError] = useState(false);
    const [showTable, setShowTable] = useState(false);
    const [notification, setNotification] = useState(false); // уведомление, что данные ушли на сервер
    const modRows = useModifiedRows();
    const notificationMessage = useRef("Ошибка при отправке данных!");
    const programImg = useRef<string | null>(null);
    // эта функция никогда не изменяется
    const dataUpdater = useMemo(() => updateTableData(columnFields, setData), []);

    const updateTable = useCallback(
        (rowId: number, processObject) => {
            modRows.updateModifiedRows(rowId);
            dataUpdater(rowId, processObject);
        },
        [dataUpdater, modRows]
    );

    const createColumns = useCallback(
        (headers: Record<string, string>) => {
            console.log("создаем колонки");
            const clmns: GridColDef[] = columnFields.map((columnname) => {
                let col: GridColDef = {
                    field: columnname,
                    headerName: headers[columnname],
                    flex: 1,
                };
                if (columnname === "part_pic") {
                    col = {
                        ...col,
                        width: 130,
                        flex: 0,
                        renderCell: (params) => <ImageWidget source={params.value} />,
                    };
                }

                if (columnname == "qty_fact") {
                    col = {
                        ...col,
                        flex: 0,
                        width: 100,
                        renderCell: (params) => (
                            <QtyInput
                                rowId={params.row.id}
                                initialQty={params.row.qty_fact}
                                assignHandler={updateTable}
                            />
                        ),
                    };
                }

                return col;
            });
            return clmns;
        },
        [updateTable]
    );

    const prepareData = (data) => {
        const prepared = data.map((row) => {
            let preparedRow = columnFields.reduce<Partial<FilteredMasterProgramParts>>((acc, field) => {
                acc[field] = row[field];
                return acc;
            }, {});
            preparedRow["part_pic"] = row.part_pic ? `${BASE_URL}${row.part_pic}` : null;
            preparedRow["fio_doers"] = row["fio_doers"].map((item) => item.fio_doer).join(", ");
            return preparedRow;
        });
        return prepared;
    };

    /**Функция загрузки данных о деталях */
    const loader = async () => {
        setShowTable(false);
        if (programInfo.programIds ===undefined) {
            throw new Error("Отсутствует идентификаторы программ для запроса")
        }
        const response = await masterGetDetailsByProgramId(programInfo.programIds);
        if (response !== undefined) {
            setData(prepareData(response.data));
            columns.current = createColumns(response.headers);
            programImg.current = response.program_pic ? `${BASE_URL}${response.program_pic}` : null;
            setShowTable(true);
        } else {
            setLoadError(true);
        }
    };

    /** При загрузке страницы загружаем данные о деталях*/
    useEffect(() => {
        loader();
    }, []); // не надо вставлять зависимости, иначе появляются внезапные перезагрузки бесконтрольные

    const sendQty: () => Promise<void> = async () => {
        const partsQty = data
            .filter((item) => modRows.modifiedRows.has(item.id))
            .map((item) => ({ id: item.id, qty_fact: item.qty_fact }));
        await logistCalculateParts(partsQty);
        setNotification(true);
        modRows.clearModifiedRows();
        loader();
    };

    const setQtyInProgress = () => {
        modRows.updateManyModifiedRows(data.map((row) => row.id));
        setData((prev) => prev.map((row) => ({ ...row, qty_fact: row.QtyInProcess })));
    };

    // не заметил ээфекта от мемоизации. Не перерисовывает даже если передаем в таблицу обычный объект
    // который должен каждый раз создаваться заново
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
                <Typography variant="h5">
                    Тестовое редактирование деталей программы № {programInfo.programName} на странице логиста
                </Typography>
                {loadError && <div>Ошибка загрузки</div>}
                {showTable && (
                    <>
                        <ImageWidget source={programImg.current} />
                        <Grid2 container spacing={3} sx={{ width: "90%" }} justifyContent={"center"}>
                            <Button variant="contained" onClick={sendQty} disabled={!modRows.modifiedRows.size}>
                                Применить введенное количество деталей
                            </Button>
                            <Button variant="contained" onClick={setQtyInProgress}>
                                ввести количество как в работе
                            </Button>
                        </Grid2>
                        <div style={{ height: 600, width: "100%" }}>
                            {/*такой подход позволяет избежать лишних перерисовок, когда параметры передаются одим объектом*/}
                            <FilteredDataGrid {...gridParams} />
                        </div>
                        <Notification
                            message={notificationMessage.current}
                            value={notification}
                            setValue={setNotification}
                        />
                    </>
                )}
            </Box>
        </>
    );
}
