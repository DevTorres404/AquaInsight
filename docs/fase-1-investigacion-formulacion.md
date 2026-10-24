# Fase I: investigación y formulación

## 1. Resumen, problema y objetivos

Se compararon KNN, SVM, Random Forest y MLP frente a Dummy para predecir is_safe a partir de 20 variables del dataset público Water Quality. De 7.999 filas originales se descartaron tres con errores en la etiqueta, quedando 7.996. La partición estratificada reservó 6.396 para entrenamiento y 1.600 para prueba. La selección utilizó validación cruzada de cinco pliegues sobre train y pipelines con escalado dentro de cada pliegue.

Se contrastó un algoritmo genético (GA) con GridSearch para optimizar Random Forest. GridSearch obtuvo la mayor media de Macro-F1 en CV (0,8979), frente a 0,8967 del GA. Se mantuvo el candidato GA por la decisión académica documentada antes del test. Su evaluación final guardada obtuvo Macro-F1 0,9044 y ROC-AUC 0,9829. Un prototipo FastAPI y React procesa perfiles nuevos y muestra alertas condicionales y límites de extrapolación.

Problema: determinar si estos modelos distinguen las dos etiquetas del dataset con mejor equilibrio que una regla mayoritaria. El alcance se limita a reproducir etiquetas, pues la procedencia analítica, las unidades y la representatividad geográfica no están completamente verificadas. Usuarios directos: estudiantes, docentes e investigadores que estudian clasificadores ambientales.

Pregunta de investigación: ¿qué desempeño y variabilidad presentan los cuatro modelos y las dos estrategias de búsqueda al clasificar is_safe mediante validación sobre train?

Objetivo general: comparar modelos de inteligencia computacional e integrar una configuración seleccionada en un prototipo académico reproducible.

Objetivos específicos: (1) documentar datos y aplicar una partición y pipelines que separen ajuste y evaluación; (2) comparar los cuatro modelos y Dummy, y contrastar GA con GridSearch; (3) evaluar una única vez el candidato fijado y demostrar tres casos e inputs inválidos.

Criterio comprobable: superar a Dummy en Macro-F1 de CV. La posible ventaja de GA sobre GridSearch se examina, sin asumirla. Estos resultados no demuestran superioridad estadística ni permiten inferir seguridad para consumo.

## 2. Fundamentos y antecedentes

KNN asigna la clase según vecinos cercanos [1]. El escalado afecta las distancias y la inferencia requiere comparar con registros almacenados. SVM busca una frontera de margen amplio y usa kernels para relaciones no lineales [2]. Ambas técnicas constituyen contrastes frente a ensambles y redes.

Random Forest combina árboles con aleatoriedad en el ajuste [3]. MLP encadena transformaciones y activaciones no lineales y aprende pesos por retropropagación [4]. La red evaluada usa capas (64,32), ReLU, Adam y parada temprana. Su desempeño se informa sin atribuir causalidad toxicológica a las relaciones aprendidas.

Los algoritmos genéticos mantienen poblaciones de candidatos y aplican selección, cruce y mutación [5]. Aquí cada individuo codifica hiperparámetros de Random Forest y su aptitud es Macro-F1 de CV. El GA no entrena los pesos de la MLP. Su búsqueda estocástica no garantiza un óptimo global ni una reducción de tiempo.

La lógica difusa permite pertenencias graduales entre cero y uno [6]. Ofrece un marco para razonar sobre categorías lingüísticas y transiciones alrededor de referencias ambientales. Se estudia como alternativa teórica; este prototipo no implementa un sistema Mamdani. El manejo práctico de incertidumbre consiste en mostrar probabilidades no calibradas, rangos de train y conflictos con comparaciones condicionales. Una probabilidad de clase y una pertenencia difusa son conceptos distintos.

Como antecedente ambiental, Grbčić y colaboradores [7] compararon ensambles, SVR y redes para predecir indicadores microbiológicos costeros, con CV y análisis espacial y temporal. Su problema es de regresión y sus métricas no se transfieren a nuestra clasificación binaria. El antecedente justifica comparar enfoques y estudiar generalización en otros contextos, no declarar un ganador universal.

## Referencias

[1] T. M. Cover y P. E. Hart, "Nearest neighbor pattern classification," IEEE Transactions on Information Theory, vol. 13, no. 1, pp. 21-27, 1967.
https://doi.org/10.1109/TIT.1967.1053964

[2] C. Cortes y V. Vapnik, "Support-vector networks," Machine Learning, vol. 20, pp. 273-297, 1995.
https://doi.org/10.1007/BF00994018

[3] L. Breiman, "Random Forests," Machine Learning, vol. 45, pp. 5-32, 2001.
https://doi.org/10.1023/A:1010933404324

[4] D. E. Rumelhart, G. E. Hinton y R. J. Williams, "Learning representations by back-propagating errors," Nature, vol. 323, pp. 533-536, 1986.
https://doi.org/10.1038/323533a0

[5] J. H. Holland, Adaptation in Natural and Artificial Systems. Cambridge, MA: MIT Press, 1992.
https://doi.org/10.7551/mitpress/1090.001.0001

[6] L. A. Zadeh, "Fuzzy sets," Information and Control, vol. 8, no. 3, pp. 338-353, 1965.
https://doi.org/10.1016/S0019-9958(65)90241-X

[7] L. Grbčić et al., "Coastal water quality prediction based on machine learning with feature interpretation and spatio-temporal analysis," arXiv:2107.03230v2, 2021. Prepublicación.
https://doi.org/10.48550/arXiv.2107.03230

[8] Organización Mundial de la Salud, Guidelines for drinking-water quality: fourth edition incorporating the first, second and third addenda. Ginebra: OMS, 2026.
https://www.who.int/publications/i/item/9789240121225

Fuentes primarias verificadas el 21/10/2026: publicaciones editoriales para [1]-[6], prepublicación identificada para [7] y documento oficial OMS para [8]. Las referencias sustentan el método y el contexto, sin transferir sus resultados a este dataset. Los metadatos de algunas referencias del borrador anterior no coincidían con los DOI y se sustituyeron.

Datos: mssmartypants, Water Quality, Kaggle. https://www.kaggle.com/datasets/mssmartypants/water-quality. Consulta inicial 20/10/2026. Resultados propios: reports/phase3_results.json y reports/phase4_selection.json.

