import { memo } from "react";
import { FormControl, MenuItem, Select, SelectChangeEvent } from "@mui/material";
import { ProgramPriorityType } from "../../pages/Logist/Logist.types";
 
    import {priorityStylesMap, backgroundOptionMap} from "../../utils/priority-color"

type ChangeDataCallback = ()=> string
type AssignData = {
    [key: string]: ChangeDataCallback;
};
type AssignHandlerType = (rowId: number, data: AssignData) => void;
type PriorityPropsType = {
    selectValue: ProgramPriorityType;
    rowId: number;
    priorityOptions: ProgramPriorityType[];
    assignHandler: AssignHandlerType;
};




const PrioritySelect = memo(({ selectValue, rowId, priorityOptions, assignHandler }: PriorityPropsType) => {
    const onChange = (event: SelectChangeEvent) => {
        assignHandler(rowId, {program_priority: ()=> event.target.value as ProgramPriorityType});
        
    };

    return (
        <FormControl sx={{ m: 1, width: 150 }} size="small">
        <Select value={selectValue} onChange={onChange} className={priorityStylesMap[selectValue]}>
            {priorityOptions.map((option) => (
                <MenuItem value={option}  key={option}>{option}</MenuItem>
                // раскрашенные опции
                //  <MenuItem value={option}  sx={{background:backgroundOptionMap[option], "&.Mui-selected":{background:backgroundOptionMap[option]}}} key={option}>{option}</MenuItem>
            ))}
        </Select>
        </FormControl>
    );
});

export default PrioritySelect;
