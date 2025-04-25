import { GridColDef, GridColumnVisibilityModel, GridRowModel } from "@mui/x-data-grid";
import styles from "./PritableDataGrid.module.css";
import { ImageWidget } from "../IamgeWidget/ImageWidget";

export type SimplePrintable = {
    rows: GridRowModel[];
    columns: GridColDef[];
    columnVisibility: GridColumnVisibilityModel;
    
};

export function SimplePrintable({ rows, columns, columnVisibility }: SimplePrintable) {
    const invisibleColumns = Object.entries(columnVisibility).filter(([, value])=> !value).map(([key,]) => key)
    const preparedColumns = columns.filter(item=> !invisibleColumns.includes(item.field) )
    console.log("невидимые колонки", preparedColumns)

    return (
        <table className={styles.table}>
            <thead className={styles.thead}>
                <tr>
                    {preparedColumns.map((item) => (
                        <th key={item.field}> {item.headerName} </th>
                    ))}
                </tr>
            </thead>
            <tbody>
                {rows.map((row) => {
                    return (
                        <tr key={row.id}>
                            {preparedColumns.map((col) => (
                                <td
                                    key={col.field}
                                    className={col.field === "part_pic" ? styles.image_cell : ""}
                                    name={col.field}
                                >
                                    {(col.renderCell && <ImageWidget source={row[col.field]} />) || row[col.field]}
                                </td>
                            ))}
                        </tr>
                    );
                })}
            </tbody>
        </table>
    );
}
