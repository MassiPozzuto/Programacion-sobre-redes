-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 25-05-2024 a las 05:33:58
-- Versión del servidor: 10.4.22-MariaDB
-- Versión de PHP: 8.1.2

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `chat`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `mensajes`
--

CREATE TABLE `mensajes` (
  `id` int(11) NOT NULL,
  `id_origen` int(11) NOT NULL,
  `mensaje` varchar(100) NOT NULL,
  `id_destino` int(11) DEFAULT NULL,
  `readed` bit(1) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `mensajes`
--

INSERT INTO `mensajes` (`id`, `id_origen`, `mensaje`, `id_destino`, `readed`, `created_at`) VALUES
(11, 7, 'Hola', NULL, NULL, '2024-05-17 23:58:21'),
(12, 5, 'Todo bien?', NULL, NULL, '2024-05-17 23:58:31'),
(13, 7, 'Este prueba es unn mogolico', 6, b'1', '2024-05-17 23:58:48'),
(14, 7, 'si amigo, vos?', NULL, NULL, '2024-05-17 23:59:09'),
(15, 5, 'bien bien', NULL, NULL, '2024-05-17 23:59:17'),
(16, 7, 'hole', NULL, NULL, '2024-05-18 05:41:01'),
(17, 6, 'Si, alto bobo', 7, b'1', '2024-05-24 23:09:29'),
(28, 7, 'hola', 5, b'1', '2024-05-24 23:47:37'),
(29, 5, 'qonda?', 7, b'1', '2024-05-24 23:47:49'),
(32, 7, 'aca tranqui, vos?', 5, NULL, '2024-05-25 00:01:32');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL,
  `username` varchar(40) NOT NULL,
  `password` varchar(50) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id`, `username`, `password`, `created_at`, `updated_at`, `deleted_at`) VALUES
(5, 'prueba', '123', '2024-05-17 19:48:12', NULL, NULL),
(6, 'Simon', '12345', '2024-05-17 19:48:52', NULL, NULL),
(7, 'Massi', '123', '2024-05-17 23:57:57', NULL, NULL);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `mensajes`
--
ALTER TABLE `mensajes`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uc_username` (`username`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `mensajes`
--
ALTER TABLE `mensajes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=37;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
