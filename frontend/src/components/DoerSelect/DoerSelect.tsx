import { useState, useMemo, useCallback } from "react";
import { DoerType } from "../../pages/Master/Master.types";
import { Select, SelectChangeEvent, MenuItem, InputLabel, Checkbox, Box, Chip } from "@mui/material";
import FormControl from "@mui/material/FormControl";
import OutlinedInput from "@mui/material/OutlinedInput";
import { Theme, useTheme } from "@mui/material/styles";
import ListItemText from "@mui/material/ListItemText";

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
    PaperProps: {
        style: {
            maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
            width: 250,
        },
    },
};

function getStyles(doerId: number, selectedDoers: number[], theme: Theme) {
    return {
        fontWeight: selectedDoers.includes(doerId)
            ? theme.typography.fontWeightMedium
            : theme.typography.fontWeightRegular,
    };
}

type DoerSelectPropsType = {
    selectValue: number[];
    rowId: number;
    doers: DoerType[];
    assignHandler: (programId: number, doerIds: Array<number>) => void;
};

const DoerSelect = ({ selectValue, rowId, doers, assignHandler }: DoerSelectPropsType) => {
    // добавление локального состояния решило проблему, когда состояние выбранных селектов в
    // родительском компоненте реагирует на все с задержкой на один такт, из-за чего последний ввод не засчитывается
    const theme = useTheme();
    const [localValue, setLocalValue] = useState<number[]>(selectValue);

    const getDoersNames = useCallback((doers: DoerType[]) => doers.map((doer) => doer.fio_doer), []);

    const doersNameList = getDoersNames(doers);

    
    
    const hadleSelectDoer = (event: SelectChangeEvent) => {
        const eventValue: number[] = event.target.value;
        setLocalValue(eventValue);
        assignHandler(rowId, eventValue);
    };

    // нужно сделать выделение опций галочками, чтобы их было видно
    // а так же загрузка в селект уже имеющихся выбранных опций
    return (
        <FormControl sx={{ m: 1, width: 300 }}>
            <InputLabel id="master-program-doers">Name</InputLabel>
            <Select
                labelId="master-program-doers"
                // sx={{ m: 1, minWidth: 200, height: 36, fontSize: 14 }}
                input={<OutlinedInput label="Name" />}
                multiple
                onChange={hadleSelectDoer}
                value={localValue}
                renderValue={(localValue) => (
                    <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
                        {doers
                            .filter((item) => localValue.includes(item.id))
                            .map((item) => <Chip key={item.id} label={item.fio_doer} />)
                        }
                    </Box>
                )}
                MenuProps={MenuProps}
            >
                {doers.map((doer) => (
                    <MenuItem value={doer.id} key={doer.id} style={getStyles(doer.id, localValue, theme)}>
                        <Checkbox checked={localValue.includes(doer.id)} />
                        <ListItemText primary={doer.fio_doer} />
                        
                    </MenuItem>
                ))}
            </Select>
        </FormControl>
    );
};

export default DoerSelect;
