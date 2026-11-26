/**
 * KIT DE VOZ · Los guiones de las llamadas (voz/guiones.json) y la política de cobranza.
 * Es la capa de DATOS del canal de voz: el esperado de cada llamada vive aquí, no en la prueba.
 * Todo es ficticio: empresa, personas, montos y fechas.
 */
import * as fs from 'fs';
import * as path from 'path';
import { Guion, Politica } from './oraculo';

export const CARPETA_VOZ = path.join(__dirname, '..', '..', 'voz');

interface ArchivoDeGuiones {
  empresa: string;
  politica: Politica;
  llamadas: Guion[];
}

const archivo: ArchivoDeGuiones = JSON.parse(fs.readFileSync(path.join(CARPETA_VOZ, 'guiones.json'), 'utf8'));

export const politicaDeCobranza: Politica = archivo.politica;
export const guionesDeVoz: Guion[] = archivo.llamadas;

export function guion(id: string): Guion {
  const encontrado = guionesDeVoz.find((g) => g.id === id);
  if (!encontrado) throw new Error(`No hay guion para la llamada ${id}. Están: ${guionesDeVoz.map((g) => g.id).join(', ')}`);
  return encontrado;
}
