import {
    Button,
    Input
} from "@material-tailwind/react";

export function UserMan() {
    return (
        <div className="grid place-items-start justify-center gap-2">
            <div className="mt-8 flex flex-col items-center justify-center gap-4 md:flex-row">
                <div className="w-80">
                    {/* @ts-ignore */}
                    <Input label="john@pork.com" />
                </div>
                <Button size="md" className="lg:w-max shrink-0" fullWidth color="gray">
                    create key
                </Button>
            </div>
        </div>
    )
}