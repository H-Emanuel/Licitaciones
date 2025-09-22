-- SE ARREGLAN ETAPAS MAL INGRESADAS --

-- INSERTAR TIPO DE MONEDA
insert into licitaciones_moneda values (5, 'UTM');

-- SCRIPT PARA REMAPEO DE ETAPAS

select tl.nombre as nombre_tipo_licitacion, e.nombre as nombre_etapa from 
licitaciones_tipolicitacion as tl join licitaciones_tipolicitacionetapa as tle 
on tle.tipo_licitacion_id=tl.id join licitaciones_etapa as e on tle.etapa_id = e.id;

alter table licitaciones_bitacoralicitacion alter column etapa_id drop not null;
alter table licitacion_licitacion alter column etapa_fk_id drop not null;

alter table licitacion_licitacion add column etapa2_fk_id bigint;
update licitacion_licitacion set etapa2_fk_id=etapa_fk_id;
update licitacion_licitacion set etapa_fk_id=null;

alter table licitaciones_bitacoralicitacion add column etapa2_id bigint;
update licitaciones_bitacoralicitacion set etapa2_id=etapa_id;
update licitaciones_bitacoralicitacion set etapa_id=null;

delete from licitaciones_etapa;
delete from licitaciones_tipolicitacionetapa;

SELECT setval('licitaciones_etapa_id_seq', 1, false);
SELECT setval('licitaciones_tipolicitacionetapa_id_seq', 1, false);

insert into licitaciones_etapa (nombre) values
('Solicitud de bases administrativas'),
('Revisar catálogo'),
('Cotización'),
('Borrador de ratificación de bases'),
('Decreto de intención de compra'),
('Evaluación de la cotización'),
('Publicación en portal'),
('Comisión de base'),
('Recepción de ofertas'),
('Disponibilidad presupuestaria'),
('Solicitud de régimen interno'),
('Publicación mercado público'),
('Evaluación de ofertas'),
('Solicitud de comisión de régimen interno'),
('Recepción de documento de régimen interno'),
('Aprobación del consejo'),
('Decreto de contratación'),
('Adjudicación'),
('Firma de contrato y orden de compra'),
('Firma de contrato'),
('Compra finalizada');




-- publica
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Solicitud de bases administrativas') where etapa2_fk_id=1;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Borrador de ratificación de bases') where etapa2_fk_id=2;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Publicación en portal') where etapa2_fk_id=3;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Recepción de ofertas') where etapa2_fk_id=4;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Disponibilidad presupuestaria') where etapa2_fk_id=5;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Evaluación de ofertas') where etapa2_fk_id=6;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Solicitud de comisión de régimen interno') where etapa2_fk_id=7;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Recepción de documento de régimen interno') where etapa2_fk_id=8;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Aprobación del consejo') where etapa2_fk_id=9;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Adjudicación') where etapa2_fk_id=10;
-- convenio marco
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Revisar catálogo') where etapa2_fk_id=11;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Decreto de intención de compra') where etapa2_fk_id=12;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Comisión de base') where etapa2_fk_id=13;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Disponibilidad presupuestaria') where etapa2_fk_id=14;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Publicación mercado público') where etapa2_fk_id=15;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Evaluación de ofertas') where etapa2_fk_id=16;
-- privada
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Solicitud de bases administrativas') where etapa2_fk_id=17;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Borrador de ratificación de bases') where etapa2_fk_id=18;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Publicación en portal') where etapa2_fk_id=19;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Recepción de ofertas') where etapa2_fk_id=20;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Disponibilidad presupuestaria') where etapa2_fk_id=21;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Evaluación de ofertas') where etapa2_fk_id=22;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Solicitud de comisión de régimen interno') where etapa2_fk_id=23;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Recepción de documento de régimen interno') where etapa2_fk_id=24;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Aprobación del consejo') where etapa2_fk_id=25;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Adjudicación') where etapa2_fk_id=26;
-- trato directo
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Cotización') where etapa2_fk_id=27;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Evaluación de la cotización') where etapa2_fk_id=28;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Disponibilidad presupuestaria') where etapa2_fk_id=29;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Solicitud de régimen interno') where etapa2_fk_id=30;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Aprobación del consejo') where etapa2_fk_id=31;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Decreto de contratación') where etapa2_fk_id=32;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Adjudicación') where etapa2_fk_id=33;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Firma de contrato') where etapa2_fk_id=34;
update licitacion_licitacion set etapa_fk_id = (select id from licitaciones_etapa where nombre='Compra finalizada') where etapa2_fk_id=35;




-- publica
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Solicitud de bases administrativas') where etapa2_id=1;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Borrador de ratificación de bases') where etapa2_id=2;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Publicación en portal') where etapa2_id=3;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Recepción de ofertas') where etapa2_id=4;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Disponibilidad presupuestaria') where etapa2_id=5;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Evaluación de ofertas') where etapa2_id=6;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Solicitud de comisión de régimen interno') where etapa2_id=7;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Recepción de documento de régimen interno') where etapa2_id=8;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Aprobación del consejo') where etapa2_id=9;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Adjudicación') where etapa2_id=10;
-- convenio marco
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Revisar catálogo') where etapa2_id=11;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Decreto de intención de compra') where etapa2_id=12;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Comisión de base') where etapa2_id=13;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Disponibilidad presupuestaria') where etapa2_id=14;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Publicación mercado público') where etapa2_id=15;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Evaluación de ofertas') where etapa2_id=16;
-- privada
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Solicitud de bases administrativas') where etapa2_id=17;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Borrador de ratificación de bases') where etapa2_id=18;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Publicación en portal') where etapa2_id=19;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Recepción de ofertas') where etapa2_id=20;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Disponibilidad presupuestaria') where etapa2_id=21;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Evaluación de ofertas') where etapa2_id=22;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Solicitud de comisión de régimen interno') where etapa2_id=23;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Recepción de documento de régimen interno') where etapa2_id=24;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Aprobación del consejo') where etapa2_id=25;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Adjudicación') where etapa2_id=26;
-- trato directo
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Cotización') where etapa2_id=27;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Evaluación de la cotización') where etapa2_id=28;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Disponibilidad presupuestaria') where etapa2_id=29;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Solicitud de régimen interno') where etapa2_id=30;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Aprobación del consejo') where etapa2_id=31;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Decreto de contratación') where etapa2_id=32;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Adjudicación') where etapa2_id=33;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Firma de contrato') where etapa2_id=34;
update licitaciones_bitacoralicitacion set etapa_id = (select id from licitaciones_etapa where nombre='Compra finalizada') where etapa2_id=35;





-- publica
insert into licitaciones_tipolicitacionetapa values ( 1, 1, (select id from licitaciones_etapa where nombre='Solicitud de bases administrativas'), 1 ),
( 2, 2, (select id from licitaciones_etapa where nombre='Borrador de ratificación de bases'), 1 ),
( 3, 3, (select id from licitaciones_etapa where nombre='Publicación en portal'), 1 ),
( 4, 4, (select id from licitaciones_etapa where nombre='Recepción de ofertas'), 1 ),
( 5, 5, (select id from licitaciones_etapa where nombre='Disponibilidad presupuestaria'), 1 ),
( 6, 6, (select id from licitaciones_etapa where nombre='Evaluación de ofertas'), 1 ),
( 7, 7, (select id from licitaciones_etapa where nombre='Solicitud de comisión de régimen interno'), 1 ),
( 8, 8, (select id from licitaciones_etapa where nombre='Recepción de documento de régimen interno'), 1 ),
( 9, 9, (select id from licitaciones_etapa where nombre='Aprobación del consejo'), 1 ),
( 10, 10, (select id from licitaciones_etapa where nombre='Adjudicación'), 1 ),
( 11, 11, (select id from licitaciones_etapa where nombre='Firma de contrato y orden de compra'), 1 ),
( 12, 12, (select id from licitaciones_etapa where nombre='Compra finalizada'), 1 );
-- convenio marco
insert into licitaciones_tipolicitacionetapa values ( 13, 1, (select id from licitaciones_etapa where nombre='Revisar catálogo'), 2 ),
( 14, 2, (select id from licitaciones_etapa where nombre='Decreto de intención de compra'), 2 ),
( 15, 3, (select id from licitaciones_etapa where nombre='Comisión de base'), 2 ),
( 16, 4, (select id from licitaciones_etapa where nombre='Disponibilidad presupuestaria'), 2 ),
( 17, 5, (select id from licitaciones_etapa where nombre='Publicación mercado público'), 2 ),
( 18, 6, (select id from licitaciones_etapa where nombre='Evaluación de ofertas'), 2 ),
( 19, 7, (select id from licitaciones_etapa where nombre='Solicitud de comisión de régimen interno'), 2 ),
( 20, 8, (select id from licitaciones_etapa where nombre='Recepción de documento de régimen interno'), 2 ),
( 21, 9, (select id from licitaciones_etapa where nombre='Aprobación del consejo'), 2 ),
( 22, 10, (select id from licitaciones_etapa where nombre='Adjudicación'), 2 ),
( 23, 11, (select id from licitaciones_etapa where nombre='Firma de contrato'), 2 ),
( 24, 12, (select id from licitaciones_etapa where nombre='Compra finalizada'), 2 );
-- privada
insert into licitaciones_tipolicitacionetapa values ( 25, 1, (select id from licitaciones_etapa where nombre='Solicitud de bases administrativas'), 3 ),
( 26, 2, (select id from licitaciones_etapa where nombre='Borrador de ratificación de bases'), 3 ),
( 27, 3, (select id from licitaciones_etapa where nombre='Publicación en portal'), 3 ),
( 28, 4, (select id from licitaciones_etapa where nombre='Recepción de ofertas'), 3 ),
( 29, 5, (select id from licitaciones_etapa where nombre='Disponibilidad presupuestaria'), 3 ),
( 30, 6, (select id from licitaciones_etapa where nombre='Evaluación de ofertas'), 3 ),
( 31, 7, (select id from licitaciones_etapa where nombre='Solicitud de comisión de régimen interno'), 3 ),
( 32, 8, (select id from licitaciones_etapa where nombre='Recepción de documento de régimen interno'), 3 ),
( 33, 9, (select id from licitaciones_etapa where nombre='Aprobación del consejo'), 3 ),
( 34, 10, (select id from licitaciones_etapa where nombre='Adjudicación'), 3 ),
( 35, 11, (select id from licitaciones_etapa where nombre='Firma de contrato y orden de compra'), 3 ),
( 36, 12, (select id from licitaciones_etapa where nombre='Compra finalizada'), 3 );
-- trato directo
insert into licitaciones_tipolicitacionetapa values ( 37, 1, (select id from licitaciones_etapa where nombre='Cotización'), 4 ),
( 38, 2, (select id from licitaciones_etapa where nombre='Evaluación de la cotización'), 4 ),
( 39, 3, (select id from licitaciones_etapa where nombre='Disponibilidad presupuestaria'), 4 ),
( 40, 4, (select id from licitaciones_etapa where nombre='Solicitud de régimen interno'), 4 ),
( 41, 5, (select id from licitaciones_etapa where nombre='Aprobación del consejo'), 4 ),
( 42, 6, (select id from licitaciones_etapa where nombre='Decreto de contratación'), 4 ),
( 43, 7, (select id from licitaciones_etapa where nombre='Adjudicación'), 4 ),
( 44, 8, (select id from licitaciones_etapa where nombre='Firma de contrato'), 4 ),
( 45, 9, (select id from licitaciones_etapa where nombre='Compra finalizada'), 4 );

alter table licitaciones_bitacoralicitacion alter column etapa_id set not null;
alter table licitacion_licitacion alter column etapa_fk_id set not null;

alter table licitacion_licitacion drop column etapa2_fk_id;
alter table licitaciones_bitacoralicitacion drop column etapa2_id;

select tl.nombre as nombre_tipo_licitacion, e.nombre as nombre_etapa from 
licitaciones_tipolicitacion as tl join licitaciones_tipolicitacionetapa as tle 
on tle.tipo_licitacion_id=tl.id join licitaciones_etapa as e on tle.etapa_id = e.id;