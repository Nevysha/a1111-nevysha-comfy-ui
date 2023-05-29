import React, {createContext, ReactNode, useState} from 'react';
import {Image} from "../../cozy-types";
// @ts-ignore
import {CozyLogger} from "../../main/CozyLogger";

interface ImagesContextType {
    images: Image[];
    setImages: React.Dispatch<React.SetStateAction<Image[]>>;
    filteredImages: Image[];
    setFilteredImages: React.Dispatch<React.SetStateAction<Image[]>>;
}

export const ImagesContext = createContext<ImagesContextType>({
    images: [],
    setImages: () => {},
    filteredImages: [],
    setFilteredImages: () => {}
});

export function ImagesProvider({ children }: { children: ReactNode[] }) {
    const [images, setImages] = useState<Image[]>([]);
    const [filteredImages, setFilteredImages] = useState<Image[]>([]);

    const value = {
        images,
        setImages,
        filteredImages,
        setFilteredImages
    }

    return (
        <ImagesContext.Provider value={value}>
            {children}
        </ImagesContext.Provider>
    )
}
