import { Grid2 } from "@mui/material";
import { LocalizationProvider, DatePicker } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { DateDiapazonType } from "../../pages/Techman/Techman.types.ts";
import dayjs, { Dayjs } from "dayjs";
import "dayjs/locale/ru";
dayjs.locale("ru");

type IDateDiapazonProps = {
    dates: DateDiapazonType;
    setDates: React.Dispatch<React.SetStateAction<DateDiapazonType>>;
};

export const DateDiapazon = ({ dates, setDates }: IDateDiapazonProps) => {
    const handleStartDate = (date: Dayjs | null) => {
        console.log("обрабатываемая начальная дата", date);
        if (dayjs.isDayjs(date)) {
            setDates({ ...dates, startDate: date });
        }
    };

    const handleEndDate = (date: Dayjs | null) => {
        console.log("обрабатываемая конечная дата", date);
        if (dayjs.isDayjs(date)) {
            setDates({ ...dates, endDate: date });
        }
    };

    return (
        <>
            <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale="ru">
                <Grid2 container spacing={2} justifyContent="center">
                    <Grid2>
                        <DatePicker
                            label="Начальная дата"
                            value={dates.startDate}
                            maxDate={dates.endDate}
                            onChange={handleStartDate}
                        />
                    </Grid2>
                    <Grid2>
                        <DatePicker
                            label="Конечная дата"
                            value={dates.endDate}
                            minDate={dates.startDate}
                            onChange={handleEndDate}
                        />
                    </Grid2>
                </Grid2>
            </LocalizationProvider>
        </>
    );
};
