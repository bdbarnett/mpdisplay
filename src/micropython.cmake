# Create an INTERFACE library for our C module.
add_library(usermod_mpdisplay INTERFACE)

# Add our source files to the lib
target_sources(usermod_mpdisplay INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/mpdisplay.c
    ${CMAKE_CURRENT_LIST_DIR}/mpdisplay_common.c
    ${CMAKE_CURRENT_LIST_DIR}/mpdisplay_esp.c
    ${CMAKE_CURRENT_LIST_DIR}/mpdisplay_esp_i80_bus.c
    ${CMAKE_CURRENT_LIST_DIR}/mpdisplay_esp_spi_bus.c
    )

# Add the current directory as an include directory.
target_include_directories(usermod_mpdisplay INTERFACE
    ${IDF_PATH}/components/esp_lcd/include/
    ${CMAKE_CURRENT_LIST_DIR}
    )

# Link our INTERFACE library to the usermod target.
target_link_libraries(usermod INTERFACE usermod_mpdisplay)
