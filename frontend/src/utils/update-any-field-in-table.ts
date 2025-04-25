type ChangeDataCallback<T = any> = (...params: any[]) => T;
type AssignData<T> = {
    [key: string]: ChangeDataCallback<T>;
};

export type UniversalUpdaterType<T> = (rowId: number, data: AssignData<T>) => void;

export function updateTableData<T, A>(
    columnFields: Array<keyof T>,
    dataSetter: React.Dispatch<React.SetStateAction<A>>
): UniversalUpdaterType<T> {
    return (rowId: number, processObject) => {
        const processFields = Object.keys(processObject);
        dataSetter((prev) =>
            prev!.map((row) => {
                if (row.id === rowId) {
                    const newRow = columnFields.reduce(
                        (acc, field) => {
                            if (processFields.includes(field)) {
                                acc[field] = processObject[field](row);
                            }
                            return acc;
                        },
                        { ...row }
                    );
                    return newRow;
                }
                return row;
            })
        );
    };
}

