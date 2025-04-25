import { GridRowModel } from "@mui/x-data-grid";

/**
 * Функция фильтрации данных в таблице по глобальному фильтру
 * @param rows оригинальные данные
 * @param filterText текст, который будет искаться в каждок ячейке
 * @returns отфильтрованный массив строк из оригинальных данных
 */
// export const filterRows = (rows: GridRowModel[], filterText: string) => {
//     const lowercasedFilter = filterText.toLowerCase();
//     if (filterText==='') return [...rows]
//     return rows.filter((row) =>
//         Object.values(row).some((value) => String(value).toLowerCase().includes(lowercasedFilter))
//     );
// };

export const filterRows = (rows: GridRowModel[], filterText: string) => {
    const lowercasedFilter = filterText.toLowerCase();
    if (filterText==='') return [...rows]
    const res = rows.filter((row) => { 
        return Object.values(row).some((value) => {
            const isContains = String(value).toLowerCase().includes(lowercasedFilter)
            return isContains
        })})
    return res
    
};

/**
 * Копирование отфильированных строк назад в оригинальные данные.
 * Здесь не отследивается, были ли отфильтрованные данные как-то изменениы.
 * По хорошему, если никаких изменений не было, то и менять оригинальные данные не нужно.
 * Наверное надо завести какую-то ссылку на отфильтрованные данные сразу после фильтрации 
 * и сравнивать их перед синхронизацией.
 * @param filteredState отфильтрованные данные
 * @param setOriginState функция для изменения оригинальных данных
 */
export const syncFiltered = (
    filteredState: GridRowModel[],
    setOriginState: React.Dispatch<React.SetStateAction<GridRowModel[]>>
) => {
    console.log("синхронизация полного и отфильтрованного объектов")
    const filteredObj = filteredState.reduce((acc, item) => {
        acc[item.id] = item;
        return acc;
    }, {});
    console.log(filteredObj);
    // нмера рядов отфильтрованных объектов
    const filteredRowIds = Object.keys(filteredObj);
    // если идентификатор оригинального ряда совпадает с идентификатором отфильтрованного ряда,
    // то копируем в оригинальный объект отфильтрованный ряд
    setOriginState((prev) =>
        prev.map((item) => {
            if (filteredRowIds.includes(item.id)) {
                console.log("измененный столбец:", item.id)
                return filteredObj[item.id]};
            return item;
        })
    );
};
