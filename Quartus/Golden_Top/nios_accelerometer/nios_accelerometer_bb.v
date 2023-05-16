
module nios_accelerometer (
	accelerometer_spi_external_interface_I2C_SDAT,
	accelerometer_spi_external_interface_I2C_SCLK,
	accelerometer_spi_external_interface_G_SENSOR_CS_N,
	accelerometer_spi_external_interface_G_SENSOR_INT,
	button_external_connection_export,
	clk_clk,
	led_external_connection_export,
	reset_reset_n,
	hex5_external_connection_export,
	hex4_external_connection_export,
	hex3_external_connection_export,
	hex2_external_connection_export,
	hex1_external_connection_export,
	hex0_external_connection_export,
	switch_external_connection_export);	

	inout		accelerometer_spi_external_interface_I2C_SDAT;
	output		accelerometer_spi_external_interface_I2C_SCLK;
	output		accelerometer_spi_external_interface_G_SENSOR_CS_N;
	input		accelerometer_spi_external_interface_G_SENSOR_INT;
	input	[3:0]	button_external_connection_export;
	input		clk_clk;
	output	[9:0]	led_external_connection_export;
	input		reset_reset_n;
	output	[6:0]	hex5_external_connection_export;
	output	[6:0]	hex4_external_connection_export;
	output	[6:0]	hex3_external_connection_export;
	output	[6:0]	hex2_external_connection_export;
	output	[6:0]	hex1_external_connection_export;
	output	[6:0]	hex0_external_connection_export;
	input	[9:0]	switch_external_connection_export;
endmodule
