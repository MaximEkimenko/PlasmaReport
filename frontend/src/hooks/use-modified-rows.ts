import { useCallback, useState } from "react";

type IdType = number | string
/**
 * Хук нужен для учета измененных строк в таблице и очистки списка измененных стролбцов
 */

export function useModifiedRows() {
    const [modifiedRows, setModifiedRows] = useState<Set<IdType>>(new Set());

    const updateModifiedRows = useCallback(
        (rowId: IdType) => {
            if (!modifiedRows.has(rowId)) {
                setModifiedRows((prev) => {
                    const next = new Set(prev);
                    next.add(rowId);
                    return next;
                });
            }
        },
        [modifiedRows]
    );

    const updateManyModifiedRows = useCallback(
        (rowIds: Array<IdType>) =>
            setModifiedRows((prev) => {
                return new Set([...prev, ...rowIds]);
            }),
        []
    );

    const removeManyModifiedRows = useCallback(
         (rowIds: Array<IdType>) =>
            setModifiedRows((prev) => {
                return new Set( [...prev].filter(item =>  !rowIds.includes(item)));
            }),
        []
    );

    const clearModifiedRows = useCallback(() => {
        setModifiedRows(new Set());
    }, []);

    return { modifiedRows, clearModifiedRows, updateModifiedRows, removeManyModifiedRows, updateManyModifiedRows };
}
