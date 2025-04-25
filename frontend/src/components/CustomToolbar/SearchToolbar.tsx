import { GridToolbarColumnsButton, GridToolbarContainer, GridToolbarFilterButton } from "@mui/x-data-grid";
import { Box, TextField } from "@mui/material";
import { memo } from "react";


export type SearchToolbarType = { filterText: string; setFilterText: React.Dispatch<React.SetStateAction<string>> };

const SearchToolbar = memo(({ filterText, setFilterText }: SearchToolbarType) =>{
    console.log("прерисовывается глобальный фильтр, значение:", filterText)
    return (
        <GridToolbarContainer>
            <GridToolbarColumnsButton />
            <GridToolbarFilterButton />
            <Box flex={1} />
            <TextField
                sx={{ flex: 1 }}
                variant="standard"
                placeholder="поиск по таблице"
                value={filterText}
                onChange={(e) => setFilterText(e.target.value)}
            />
        </GridToolbarContainer>
    );
})

export default SearchToolbar;
